import logging

from app.databases.memory import CompanyData
from app.ingestion.gmail_ingestion import EmailIngestion
from app.service.feedback_analyzer import FeedbackAnalyzer


logger = logging.getLogger(__name__)


class GmailSyncService:

    def __init__(self):

        self.gmail = EmailIngestion(
            query="is:unread",
            max_messages=10,
        )

        self.company_data = CompanyData()

        self.feedback_analyzer = FeedbackAnalyzer()

    def sync(self) -> dict:

        emails = self.gmail.ingest_all()

        stored = 0
        skipped = 0
        unmatched = 0
        analyzed = 0
        feedback_created = 0
        analysis_failed = 0

        for email in emails:

            gmail_message_id = email["gmail_message_id"]

            # --------------------------------------------------
            # 1. Check whether email already exists
            # --------------------------------------------------

            existing = (
                self.company_data.get_email_by_gmail_id(
                    gmail_message_id
                )
            )

            if existing:

                skipped += 1

                logger.info(
                    "Skipping already stored email: %s",
                    gmail_message_id,
                )

                continue

            # --------------------------------------------------
            # 2. Match sender with customer
            # --------------------------------------------------

            customer = self.company_data.get_customer(
                email["sender_email"]
            )

            customer_id = (
                customer.id
                if customer
                else None
            )

            if not customer:

                unmatched += 1

                logger.warning(
                    "No customer found for sender: %s",
                    email["sender_email"],
                )

            # --------------------------------------------------
            # 3. Store email
            # --------------------------------------------------

            stored_email = (
                self.company_data.add_email_message(
                    gmail_message_id=email[
                        "gmail_message_id"
                    ],
                    thread_id=email["thread_id"],
                    customer_id=customer_id,
                    sender_name=email["sender_name"],
                    sender_email=email["sender_email"],
                    recipient=email["recipient"],
                    cc=email["cc"],
                    subject=email["subject"],
                    body=email["body"],
                    received_at=email["received_at"],
                    labels=",".join(
                        email["labels"]
                    ),
                )
            )

            stored += 1

            # --------------------------------------------------
            # 4. Only analyze emails belonging to customers
            # --------------------------------------------------

            if not customer_id:

                continue

            # --------------------------------------------------
            # 5. Analyze email with Gemini
            # --------------------------------------------------

            try:

                analysis = (
                    self.feedback_analyzer.analyze_email(
                        subject=email["subject"],
                        body=email["body"],
                    )
                )

                analyzed += 1

                logger.info(
                    "Feedback analysis for email %s: %s",
                    gmail_message_id,
                    analysis,
                )

            except Exception:

                analysis_failed += 1

                logger.exception(
                    "Feedback analysis failed for email %s",
                    gmail_message_id,
                )

                # Email is already stored.
                # Do not lose it because Gemini failed.
                continue

            # --------------------------------------------------
            # 6. Check whether this is actually feedback
            # --------------------------------------------------

            if not analysis["is_feedback"]:

                logger.info(
                    "Email %s is not customer feedback.",
                    gmail_message_id,
                )

                continue

            # --------------------------------------------------
            # 7. Prevent duplicate feedback
            # --------------------------------------------------

            existing_feedback = (
                self.company_data.get_feedback_by_email_id(
                    stored_email.id
                )
            )

            if existing_feedback:

                logger.info(
                    "Feedback already exists for email %s",
                    gmail_message_id,
                )

                continue

            # --------------------------------------------------
            # 8. Store structured feedback
            # --------------------------------------------------

            self.company_data.add_customer_feedback(

                customer_id=customer_id,

                email_message_id=stored_email.id,

                rating=analysis["rating"],

                subject=analysis["subject"],

                comments=analysis["comments"],
            )

            feedback_created += 1

            logger.info(
                "Customer feedback created for email %s",
                gmail_message_id,
            )

        return {
            "success": True,
            "found": len(emails),
            "stored": stored,
            "skipped": skipped,
            "unmatched": unmatched,
            "analyzed": analyzed,
            "feedback_created": feedback_created,
            "analysis_failed": analysis_failed,
        }