from app.service.feedback_analyzer import FeedbackAnalyzer


def main():
    analyzer = FeedbackAnalyzer()

    subject = "Problem with product F"

    body = """
We've been using Product F for the last few weeks.
The dashboard is very slow and sometimes doesn't load.
This is causing problems for our team.
Please fix this issue.
"""

    result = analyzer.analyze_email(
        subject=subject,
        body=body,
    )

    print("\nGemini Feedback Analysis:")
    print(result)


if __name__ == "__main__":
    main()