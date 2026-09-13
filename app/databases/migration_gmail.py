from sqlalchemy import text

from app.databases.db import engine


def migrate():
    with engine.begin() as connection:

        # Remove the incorrect foreign key.
        connection.execute(
            text(
                """
                ALTER TABLE email_messages
                DROP CONSTRAINT IF EXISTS
                email_messages_customer_id_fkey;
                """
            )
        )

        # Point email_messages.customer_id to
        # the existing customers table.
        connection.execute(
            text(
                """
                ALTER TABLE email_messages
                ADD CONSTRAINT email_messages_customer_id_fkey
                FOREIGN KEY (customer_id)
                REFERENCES customers(id);
                """
            )
        )

        # Add the feedback → email relationship.
        connection.execute(
            text(
                """
                ALTER TABLE customer_feedback
                DROP CONSTRAINT IF EXISTS
                customer_feedback_email_message_id_fkey;
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE customer_feedback
                ADD CONSTRAINT
                customer_feedback_email_message_id_fkey
                FOREIGN KEY (email_message_id)
                REFERENCES email_messages(id);
                """
            )
        )


if __name__ == "__main__":
    migrate()
    print("Gmail database migration completed.")