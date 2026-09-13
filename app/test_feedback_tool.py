from app.tools.feedback_tool import FeedbackTools


def main():
    tool = FeedbackTools()

    result = tool.get_customer_feedback_by_email_id(
        email_message_id=14
    )

    print("\nCustomer Feedback:")
    print(result)


if __name__ == "__main__":
    main()