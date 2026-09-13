from app.databases.memory import CompanyData
from app.databases.models import FeedbackRating


def main():
    company_data = CompanyData()

    # Get the email we just synchronized
    email = company_data.get_email_by_gmail_id(
        "1a07a8a0c147eec2"
    )

    if not email:
        print("Email not found.")
        return

    print("Email found:")
    print("ID:", email.id)
    print("Customer ID:", email.customer_id)
    print("Subject:", email.subject)

    if not email.customer_id:
        print("This email is not associated with a customer.")
        return

    # Prevent duplicate feedback
    existing = company_data.get_feedback_by_email_id(
        email.id
    )

    if existing:
        print("Feedback already exists:", existing.id)
        return

    feedback = company_data.add_customer_feedback(
        customer_id=email.customer_id,
        email_message_id=email.id,
        rating=FeedbackRating.BAD,
        subject="Product F dashboard performance",
        comments=(
            "Customer reports that the Product F dashboard "
            "is very slow and sometimes fails to load, "
            "causing problems for their team."
        ),
    )

    print("\nFeedback created successfully!")
    print("Feedback ID:", feedback.id)
    print("Customer ID:", feedback.customer_id)
    print("Email Message ID:", feedback.email_message_id)
    print("Rating:", feedback.rating)
    print("Subject:", feedback.subject)
    print("Comments:", feedback.comments)


if __name__ == "__main__":
    main()