import logging

from app.service.gmail_sync import GmailSyncService


logging.basicConfig(
    level=logging.INFO,
)


def main():

    print("1. Creating GmailSyncService...", flush=True)

    service = GmailSyncService()

    print("2. Starting Gmail sync...", flush=True)

    result = service.sync()

    print("3. Gmail sync completed!", flush=True)

    print(result, flush=True)


if __name__ == "__main__":
    main()