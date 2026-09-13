import base64
import logging
from datetime import datetime
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


logger = logging.getLogger(__name__)


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

TOKEN_FILE = Path("token.json")
CREDENTIALS_FILE = Path("credentials.json")


class EmailIngestion:

    def __init__(
    self,
    token_file: Path = TOKEN_FILE,
    credentials_file: Path = CREDENTIALS_FILE,
    query: str = "is:unread",
    max_messages: int = 100,
    ):
     self.token_file = token_file
     self.credentials_file = credentials_file
     self.query = query
     self.max_messages = max_messages

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------

    def authenticate(self):

        creds = None

        # Load previously saved credentials
        if self.token_file.exists():

            creds = Credentials.from_authorized_user_file(
                str(self.token_file),
                SCOPES,
            )

        # Refresh expired credentials
        if creds and creds.expired and creds.refresh_token:

            logger.info("Refreshing Gmail OAuth token.")

            creds.refresh(Request())

            self.token_file.write_text(
                creds.to_json(),
                encoding="utf-8",
            )

        # First-time authentication
        elif not creds or not creds.valid:

            if not self.credentials_file.exists():

                raise FileNotFoundError(
                    f"Google OAuth credentials not found: "
                    f"{self.credentials_file}"
                )

            logger.info("Starting Gmail OAuth authentication.")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file),
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

            self.token_file.write_text(
                creds.to_json(),
                encoding="utf-8",
            )

        return build(
            "gmail",
            "v1",
            credentials=creds,
            cache_discovery=False,
        )

    # ---------------------------------------------------------
    # BASE64 DECODING
    # ---------------------------------------------------------

    @staticmethod
    def decode_body(data: str) -> str:

        if not data:
            return ""

        # Gmail uses URL-safe base64.
        # Add padding if necessary.
        padding = "=" * (-len(data) % 4)

        decoded = base64.urlsafe_b64decode(
            data + padding
        )

        return decoded.decode(
            "utf-8",
            errors="replace",
        )

    # ---------------------------------------------------------
    # HEADERS
    # ---------------------------------------------------------

    @staticmethod
    def get_headers(payload: dict) -> dict:

        headers = {}

        for header in payload.get("headers", []):

            name = header.get("name", "").lower()
            value = header.get("value", "")

            headers[name] = value

        return headers

    # ---------------------------------------------------------
    # EMAIL BODY
    # ---------------------------------------------------------

    def extract_body(self, payload: dict) -> str:

        body = payload.get("body", {})

        data = body.get("data")

        if data:

            return self.decode_body(data)

        parts = payload.get("parts", [])

        # Prefer plain text
        for part in parts:

            mime_type = part.get("mimeType")

            if mime_type == "text/plain":

                data = part.get("body", {}).get("data")

                if data:

                    return self.decode_body(data)

        # Recursively search nested MIME parts
        for part in parts:

            if part.get("parts"):

                body = self.extract_body(part)

                if body:

                    return body

        return ""

    # ---------------------------------------------------------
    # PARSE DATE
    # ---------------------------------------------------------

    @staticmethod
    def parse_date(value: str | None) -> datetime | None:

        if not value:
            return None

        try:

            return parsedate_to_datetime(value)

        except (TypeError, ValueError):

            logger.warning(
                "Unable to parse email date: %s",
                value,
            )

            return None

    # ---------------------------------------------------------
    # PARSE MESSAGE
    # ---------------------------------------------------------

    def parse_message(self, message: dict) -> dict:

        payload = message.get("payload", {})

        headers = self.get_headers(payload)

        sender_name, sender_email = parseaddr(
            headers.get("from", "")
        )

        return {
            "gmail_message_id": message.get("id"),
            "thread_id": message.get("threadId"),

            "sender_name": sender_name,
            "sender_email": sender_email.lower().strip(),

            "recipient": headers.get("to"),
            "cc": headers.get("cc"),

            "subject": headers.get("subject"),

            "body": self.extract_body(payload),

            "received_at": self.parse_date(
                headers.get("date")
            ),

            "labels": message.get(
                "labelIds",
                [],
            ),
        }

    # ---------------------------------------------------------
    # INGEST ALL EMAILS
    # ---------------------------------------------------------

    def ingest_all(self) -> list[dict]:

      service = self.authenticate()

      emails = []

      page_token = None

      while len(emails) < self.max_messages:

        remaining = self.max_messages - len(emails)

        result = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=self.query,
                maxResults=min(100, remaining),
                pageToken=page_token,
            )
            .execute()
        )

        messages = result.get("messages", [])

        logger.info(
            "Found %d Gmail message(s) in this page.",
            len(messages),
        )

        for msg in messages:

            if len(emails) >= self.max_messages:
                break

            message_id = msg.get("id")

            if not message_id:
                continue

            try:

                message = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=message_id,
                        format="full",
                    )
                    .execute()
                )

                emails.append(
                    self.parse_message(message)
                )

            except Exception:

                logger.exception(
                    "Failed to process Gmail message %s",
                    message_id,
                )

        page_token = result.get("nextPageToken")

        if not page_token or not messages:
            break

      logger.info(
        "Successfully ingested %d email(s).",
        len(emails),
    )

      return emails