from typing import Optional

from sqlmodel import Session, select

from app.databases.db import engine
from app.databases.models import Deal


class DealTool:

    def get_deal(
        self,
        deal_id: Optional[int] = None
    ) -> Optional[dict]:

        if deal_id is None:
            return None

        with Session(engine) as session:

            statement = (
                select(Deal)
                .where(Deal.id == deal_id)
            )

            deal = session.exec(statement).first()

            if not deal:
                return None

            return {
                "deal_id": deal.id,
                "customer_id": deal.customer_id,
                "owner_id": deal.owner_id,
                "title": deal.title,
                "stage": deal.stage.value,
                "amount": float(deal.amount),
                "probability": deal.probability,
                "expected_close_date": (
                    deal.expected_close_date.isoformat()
                    if deal.expected_close_date
                    else None
                ),
                "actual_close_date": (
                    deal.actual_close_date.isoformat()
                    if deal.actual_close_date
                    else None
                ),
                "notes": deal.notes,
            }