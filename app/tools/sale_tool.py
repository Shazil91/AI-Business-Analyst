from datetime import date
from typing import Optional

from sqlmodel import Session, select, func

from app.databases.db import engine
from app.databases.models import (
    Sale,
    Customer,
    Product,
    User,
)


class SalesTools:
    """
    Business tools for querying sales data.

    All database access is performed through SQLModel sessions.
    """

    # =========================================================
    # GET ALL SALES
    # =========================================================

    def get_sales(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:

        with Session(engine) as session:

            statement = select(Sale)

            if start_date is not None:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date is not None:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            statement = statement.order_by(
                Sale.sale_date.desc()
            )

            sales = session.exec(statement).all()

            return [
                {
                    "sale_id": sale.id,
                    "customer_id": sale.customer_id,
                    "product_id": sale.product_id,
                    "salesperson_id": sale.salesperson_id,
                    "deal_id": sale.deal_id,
                    "sale_date": sale.sale_date.isoformat(),
                    "quantity": int(sale.quantity),
                    "unit_price": float(sale.unit_price),
                    "discount": float(sale.discount),
                    "revenue": float(sale.revenue),
                }
                for sale in sales
            ]

    # =========================================================
    # SALES BY PRODUCT
    # =========================================================

    def get_sales_by_product(
        self,
        product_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:

        with Session(engine) as session:

            statement = (
                select(
                    Sale.product_id,
                    Product.name,
                    Product.sku,
                    Sale.quantity,
                    Sale.revenue,
                )
                .join(
                    Product,
                    Sale.product_id == Product.id,
                )
            )

            if product_id is not None:
                statement = statement.where(
                    Sale.product_id == product_id
                )

            if start_date is not None:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date is not None:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            statement = statement.order_by(
                Sale.sale_date.desc()
            )

            results = session.exec(statement).all()

            return [
                {
                    "product_id": row_product_id,
                    "product_name": product_name,
                    "sku": sku,
                    "quantity": int(quantity),
                    "revenue": float(revenue),
                }
                for (
                    row_product_id,
                    product_name,
                    sku,
                    quantity,
                    revenue,
                ) in results
            ]

    # =========================================================
    # SALES BY CUSTOMER
    # =========================================================

    def get_sales_by_customer(
        self,
        customer_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:

        with Session(engine) as session:

            statement = (
                select(
                    Sale.customer_id,
                    Customer.name,
                    Customer.company_name,
                    Sale.quantity,
                    Sale.revenue,
                )
                .join(
                    Customer,
                    Sale.customer_id == Customer.id,
                )
            )

            if customer_id is not None:
                statement = statement.where(
                    Sale.customer_id == customer_id
                )

            if start_date is not None:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date is not None:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            statement = statement.order_by(
                Sale.sale_date.desc()
            )

            results = session.exec(statement).all()

            return [
                {
                    "customer_id": row_customer_id,
                    "customer_name": customer_name,
                    "company_name": company_name,
                    "quantity": int(quantity),
                    "revenue": float(revenue),
                }
                for (
                    row_customer_id,
                    customer_name,
                    company_name,
                    quantity,
                    revenue,
                ) in results
            ]

    # =========================================================
    # SALES BY SALESPERSON
    # =========================================================

    def get_sales_by_salesperson(
        self,
        salesperson_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:

        with Session(engine) as session:

            statement = (
                select(
                    Sale.salesperson_id,
                    User.name,
                    Sale.quantity,
                    Sale.revenue,
                )
                .join(
                    User,
                    Sale.salesperson_id == User.id,
                )
            )

            if salesperson_id is not None:
                statement = statement.where(
                    Sale.salesperson_id == salesperson_id
                )

            if start_date is not None:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date is not None:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            statement = statement.order_by(
                Sale.sale_date.desc()
            )

            results = session.exec(statement).all()

            return [
                {
                    "salesperson_id": row_salesperson_id,
                    "salesperson_name": salesperson_name,
                    "quantity": int(quantity),
                    "revenue": float(revenue),
                }
                for (
                    row_salesperson_id,
                    salesperson_name,
                    quantity,
                    revenue,
                ) in results
            ]

    # =========================================================
    # SALES BY REGION
    # =========================================================

    def get_sales_by_region(
        self,
        region: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:

        if not isinstance(region, str):
            raise TypeError(
                "region must be a string."
            )

        region = region.strip()

        if not region:
            raise ValueError(
                "region cannot be empty."
            )

        with Session(engine) as session:

            statement = (
                select(
                    Customer.region,
                    func.coalesce(
                        func.sum(Sale.revenue),
                        0,
                    ).label("revenue"),
                    func.coalesce(
                        func.sum(Sale.quantity),
                        0,
                    ).label("quantity"),
                )
                .join(
                    Sale,
                    Sale.customer_id == Customer.id,
                )
                .where(
                    Customer.region == region
                )
                .group_by(
                    Customer.region
                )
            )

            if start_date is not None:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date is not None:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            result = session.exec(statement).first()

            if result is None:
                return {
                    "region": region,
                    "revenue": 0.0,
                    "quantity": 0,
                }

            return {
                "region": result[0] or region,
                "revenue": float(result[1] or 0),
                "quantity": int(result[2] or 0),
            }

    # =========================================================
    # TOTAL SALES
    # =========================================================

    def get_total_sales(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:

        with Session(engine) as session:

            statement = select(
                func.coalesce(
                    func.sum(Sale.revenue),
                    0,
                ).label("total_revenue"),
                func.coalesce(
                    func.sum(Sale.quantity),
                    0,
                ).label("total_quantity"),
                func.count(Sale.id).label("total_transactions"),
            )

            if start_date is not None:
                statement = statement.where(
                    Sale.sale_date >= start_date
                )

            if end_date is not None:
                statement = statement.where(
                    Sale.sale_date <= end_date
                )

            result = session.exec(statement).first()

            return {
                "total_revenue": float(result[0] or 0),
                "total_quantity": int(result[1] or 0),
                "total_transactions": int(result[2] or 0),
            }