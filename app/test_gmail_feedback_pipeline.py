from app.service.gmail_sync import GmailSyncService


def main():

    print("Starting Gmail → Feedback pipeline...\n")

    service = GmailSyncService()

    result = service.sync()

    print("\nPipeline result:")
    print(result)


if __name__ == "__main__":
    main()