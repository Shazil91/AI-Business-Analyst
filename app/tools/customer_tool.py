from datetime import date
from typing import Optional

from sqlmodel import Session, select, func

from app.databases.db import engine
from app.databases.models import Customer, Sale


class CustomerTools:

    def get_customer(
        self,
        customer_id: Optional[int] = None,
        email: Optional[str] = None,
    ) -> Optional[dict]:

        if customer_id is None and email is None:
            return None

        with Session(engine) as session:

            statement = select(Customer)

            if customer_id is not None:
                statement = statement.where(
                    Customer.id == customer_id
                )
            else:
                statement = statement.where(
                    Customer.email == email
                )

            customer = session.exec(
                statement
            ).first()

            if not customer:
                return None

            return {
                "customer_id": customer.id,
                "name": customer.name,
                "company_name": customer.company_name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
                "city": customer.city,
                "country": customer.country,
                "region": customer.region,
                "industry": customer.industry,
                "notes": customer.notes,
                "owner_id": customer.owner_id,
                "created_at": (
                    customer.created_at.isoformat()
                    if customer.created_at
                    else None
                ),
                "updated_at": (
                    customer.updated_at.isoformat()
                    if customer.updated_at
                    else None
                ),
            }

    def get_top_customers(
        self,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:

        if limit < 1 or limit > 100:
            raise ValueError(
                "limit must be between 1 and 100."
            )

        if (
            start_date
            and end_date
            and start_date > end_date
        ):
            raise ValueError(
                "start_date cannot be after end_date."
            )

        with Session(engine) as session:

            statement = (
                select(
                    Customer.id,
                    Customer.name,
                    Customer.company_name,
                    func.coalesce(
                        func.sum(Sale.revenue),
                        0,
                    ).label("total_revenue"),
                )
                .join(
                    Sale,
                    Sale.customer_id == Customer.id,
                )
            )

            if start_date:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            statement = (
                statement
                .group_by(
                    Customer.id,
                    Customer.name,
                    Customer.company_name,
                )
                .order_by(
                    func.coalesce(
                        func.sum(Sale.revenue),
                        0,
                    ).desc()
                )
                .limit(limit)
            )

            results = session.exec(
                statement
            ).all()

            return [
                {
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "company_name": company_name,
                    "total_revenue": float(
                        total_revenue or 0
                    ),
                }
                for (
                    customer_id,
                    customer_name,
                    company_name,
                    total_revenue,
                ) in results
            ]

    def get_customer_revenue(
        self,
        customer_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:

        if (
            start_date
            and end_date
            and start_date > end_date
        ):
            raise ValueError(
                "start_date cannot be after end_date."
            )

        with Session(engine) as session:

            join_conditions = [
                Sale.customer_id == Customer.id
            ]

            if start_date:
                join_conditions.append(
                    Sale.sale_date >= start_date
                )

            if end_date:
                join_conditions.append(
                    Sale.sale_date <= end_date
                )

            statement = (
                select(
                    Customer.id,
                    Customer.name,
                    Customer.company_name,
                    func.coalesce(
                        func.sum(Sale.revenue),
                        0,
                    ).label("total_revenue"),
                )
                .outerjoin(
                    Sale,
                    *join_conditions,
                )
                .where(
                    Customer.id == customer_id
                )
                .group_by(
                    Customer.id,
                    Customer.name,
                    Customer.company_name,
                )
            )

            result = session.exec(
                statement
            ).first()

            if not result:
                return {
                    "customer_id": customer_id,
                    "total_revenue": 0.0,
                }

            (
                customer_id,
                customer_name,
                company_name,
                total_revenue,
            ) = result

            return {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "company_name": company_name,
                "total_revenue": float(
                    total_revenue or 0
                ),
            }