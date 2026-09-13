from __future__ import annotations

from typing import Any

from app.databases.memory import CompanyData
from app.databases.models import FeedbackRating


class FeedbackTools:
    """
    Business tools for retrieving customer feedback
    stored in PostgreSQL.
    """

    def __init__(self):
        self.company_data = CompanyData()
    
    
    def get_customer_feedback_by_email_id(
        self,
        email_message_id: int,
    ) -> dict[str, Any] | None:
        """
        Return customer feedback associated with
        a specific email message ID.
        """

        feedback = self.company_data.get_feedback_by_email_id(
            email_message_id=email_message_id
        )

        if not feedback:
            return None

        return {
            "feedback_id": feedback.id,
            "customer_id": feedback.customer_id,
            "email_message_id": feedback.email_message_id,
            "rating": (
                feedback.rating.value
                if isinstance(feedback.rating, FeedbackRating)
                else str(feedback.rating)
            ),
            "subject": feedback.subject,
            "comments": feedback.comments,
            "submitted_at": (
                feedback.submitted_at.isoformat()
                if feedback.submitted_at
                else None
            ),
        }
    
    def get_feedback_summary(
    self,
    limit: int = 50,
) -> list[dict[str, Any]]:
     """
      Return recent customer feedback for business-level analysis.
     """

     feedback_list = self.company_data.get_recent_customer_feedback(
        limit=limit
    )

     return [
        {
            "feedback_id": feedback.id,
            "customer_id": feedback.customer_id,
            "email_message_id": feedback.email_message_id,
            "rating": (
                feedback.rating.value
                if isinstance(
                    feedback.rating,
                    FeedbackRating,
                )
                else str(feedback.rating)
            ),
            "subject": feedback.subject,
            "comments": feedback.comments,
            "submitted_at": (
                feedback.submitted_at.isoformat()
                if feedback.submitted_at
                else None
            ),
        }
        for feedback in feedback_list
    ]
    
    # def get_customer_feedback(
    #     self,
    #     customer_id: int,
    # ) -> list[dict[str, Any]]:
    #     """
    #     Return feedback submitted by a specific customer.
    #     """

    #     feedback_list = (
    #         self.company_data.get_customer_feedback(
    #             customer_id=customer_id
    #         )
    #     )
        
        
    #     return [
    #         {
    #             "feedback_id": feedback.id,
    #             "customer_id": feedback.customer_id,
    #             "email_message_id": feedback.email_message_id,
    #             "rating": (
    #                 feedback.rating.value
    #                 if isinstance(
    #                     feedback.rating,
    #                     FeedbackRating,
    #                 )
    #                 else str(feedback.rating)
    #             ),
    #             "subject": feedback.subject,
    #             "comments": feedback.comments,
    #             "submitted_at": (
    #                 feedback.submitted_at.isoformat()
    #                 if feedback.submitted_at
    #                 else None
    #             ),
    #         }
    #         for feedback in feedback_list
    #     ]