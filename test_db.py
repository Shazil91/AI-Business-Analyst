from sqlmodel import Session, select

from app.databases.models import Customers
from app.databases.db import engine


with Session(engine) as session:
    customers = session.exec(
        select(Customers)
    ).all()

    print("Customers:", len(customers))

    for customer in customers[:5]:
        print(customer)