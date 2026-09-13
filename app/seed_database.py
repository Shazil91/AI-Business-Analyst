from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlmodel import Session, SQLModel, select

from app.databases.db import engine
from app.databases.models import User, Customer, Product, Sale, UserRole


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_FILE = PROJECT_ROOT / "app" / "csv" / "sales_mock_data_1200_rows.csv"


def seed_database():

    print("Creating database tables...")

    SQLModel.metadata.create_all(engine)

    print("Reading CSV...")

    df = pd.read_csv(CSV_FILE)

    print(f"Found {len(df)} sales records.")

    with Session(engine) as session:

        # --------------------------------------------------
        # 1. USERS / SALESPERSONS
        # --------------------------------------------------

        salesperson_names = df["salesperson"].unique()

        users = {}

        for name in salesperson_names:

            existing_user = session.exec(
                select(User).where(User.name == name)
            ).first()

            if existing_user:
                user = existing_user

            else:
                user = User(
                    name=name,
                    email=f"{name.lower()}@example.com",
                    password_hash="seeded-user",
                    role=UserRole.SALES,
                    is_active=True,
                )

                session.add(user)
                session.flush()

            users[name] = user


        # --------------------------------------------------
        # 2. PRODUCTS
        # --------------------------------------------------

        product_names = df["product"].unique()

        products = {}

        for product_name in product_names:

            existing_product = session.exec(
                select(Product).where(
                    Product.name == product_name
                )
            ).first()

            if existing_product:
                product = existing_product

            else:
                product = Product(
                    name=product_name,
                    sku=product_name.replace(" ", "-").upper(),
                    description=f"{product_name} product",
                    price=Decimal("0"),
                    cost=Decimal("0"),
                    stock_quantity=0,
                    is_active=True,
                )

                session.add(product)
                session.flush()

            products[product_name] = product


        # --------------------------------------------------
        # 3. CUSTOMERS
        # --------------------------------------------------
        #
        # Your CSV doesn't contain a customer column.
        #
        # Therefore we create demo customers and distribute
        # the sales records among them.
        # --------------------------------------------------

        customers = []

        existing_customers = session.exec(
            select(Customer)
        ).all()

        if existing_customers:

            customers = existing_customers

        else:

            for i in range(1, 101):

                customer = Customer(
                    name=f"Customer {i}",
                    company_name=f"Company {i}",
                    email=f"customer{i}@example.com",
                    region=df.iloc[(i - 1) % len(df)]["region"],
                    country="Pakistan",
                    industry="Technology",
                )

                session.add(customer)
                customers.append(customer)

            session.flush()


        # --------------------------------------------------
        # 4. SALES
        # --------------------------------------------------

        existing_sales = session.exec(
            select(Sale)
        ).first()

        if existing_sales:

            print("Sales already exist. Skipping sales insertion.")

        else:

            for index, row in df.iterrows():

                customer = customers[index % len(customers)]

                product = products[row["product"]]

                salesperson = users[row["salesperson"]]

                sale = Sale(
                    customer_id=customer.id,
                    salesperson_id=salesperson.id,
                    product_id=product.id,
                    sale_date=pd.to_datetime(
                        row["date"]
                    ).date(),
                    quantity=int(row["units"]),
                    unit_price=(
                        Decimal(str(row["revenue"]))
                        / Decimal(str(row["units"]))
                    ),
                    discount=Decimal("0"),
                    revenue=Decimal(
                        str(row["revenue"])
                    ),
                )

                session.add(sale)


        # --------------------------------------------------
        # COMMIT
        # --------------------------------------------------

        session.commit()

        print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()