from datetime import date
from decimal import Decimal
from sqlmodel import Session, select, func
from app.databases.db import engine
from app.databases.models import Sale

class KPITools:

    def total_revenue(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:

        with Session(engine) as session:

            statement = select(
                func.coalesce(
                    func.sum(Sale.revenue),
                    0
                )
            ).where(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            
            revenue = session.exec(
                statement
            ).one()

        return {
            "metric": "total_revenue",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "value": float(revenue or 0),
        }

    def total_units_sold(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:

        with Session(engine) as session:

            statement = select(
                func.coalesce(
                    func.sum(Sale.quantity),
                    0
                )
            ).where(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )

            units = session.exec(
                statement
            ).one()

        return {
            "metric": "total_units_sold",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "value": int(units or 0),
        }

    def average_order_value(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:

        with Session(engine) as session:

            statement = select(
                func.count(Sale.id),
                func.coalesce(
                    func.sum(Sale.revenue),
                    0
                )
            ).where(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )

            count, revenue = session.exec(
                statement
            ).one()

        count = count or 0
        revenue = revenue or Decimal("0")

        aov = (
            revenue / count
            if count > 0
            else Decimal("0")
        )

        return {
            "metric": "average_order_value",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "value": float(aov),
        }