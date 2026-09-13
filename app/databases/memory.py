from __future__ import annotations
from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Iterator, Optional
from sqlmodel import Session, select
from app.databases.db import engine
from app.databases.models import (
    Activity,
    ActivityType,
    Contact,
    Customer,
    CustomerFeedback,
    Deal,
    DealProduct,
    DealStage,
    FeedbackRating,
    Lead,
    LeadStatus,
    Product,
    Sale,
    User,
    UserRole,
    EmailMessage

)


# ============================================================================
# HELPERS
# ============================================================================

def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def _require_non_empty(value: str, field_name: str) -> str:
    """Validate required string fields."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return value.strip()


def _normalize_optional(value: Optional[str]) -> Optional[str]:
    """Normalize optional string values."""
    if value is None:
        return None

    value = value.strip()

    return value or None


def _normalize_email(email: Optional[str]) -> Optional[str]:
    """Normalize email addresses."""
    email = _normalize_optional(email)

    if email is None:
        return None

    return email.lower()


def _validate_non_negative(
    value: Decimal,
    field_name: str,
) -> None:
    if value < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )


def _validate_percentage(
    value: Decimal | int | float,
    field_name: str,
) -> None:
    if not 0 <= value <= 100:
        raise ValueError(
            f"{field_name} must be between 0 and 100."
        )


def _validate_positive(
    value: int,
    field_name: str,
) -> None:
    if value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Create a database session with safe transaction handling.

    expire_on_commit=False prevents returned SQLModel objects from
    becoming unusable after the session closes.
    """
    session = Session(
        engine,
        expire_on_commit=False,
    )

    try:
        yield session

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


# ============================================================================
# COMPANY DATA
# ============================================================================

class CompanyData:

    # ========================================================================
    # USERS
    # ========================================================================

    def add_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.SALES,
    ) -> User:

        name = _require_non_empty(
            name,
            "Name",
        )

        email = _normalize_email(email)

        if not email:
            raise ValueError(
                "Email cannot be empty."
            )

        password_hash = _require_non_empty(
            password_hash,
            "Password hash",
        )

        with get_session() as session:

            existing_user = session.exec(
                select(User).where(
                    User.email == email
                )
            ).first()

            if existing_user:
                raise ValueError(
                    f"User with email '{email}' already exists."
                )

            now = utc_now()
        
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                role=role,
                created_at=now,
                updated_at=now,
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

    def get_user(
        self,
        email: str,
    ) -> Optional[User]:

        email = _normalize_email(email)

        if not email:
            return None

        with get_session() as session:

            statement = select(User).where(
                User.email == email
            )

            return session.exec(statement).first()

    def get_user_by_id(
        self,
        user_id: int,
    ) -> Optional[User]:

        if user_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                User,
                user_id,
            )

    # ========================================================================
    # CUSTOMERS
    # ========================================================================

    def add_customer(
        self,
        name: str,
        company_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        notes: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> Customer:

        name = _require_non_empty(
            name,
            "Customer name",
        )

        email = _normalize_email(email)

        with get_session() as session:

            if email:

                existing_customer = session.exec(
                    select(Customer).where(
                        Customer.email == email
                    )
                ).first()

                if existing_customer:
                    raise ValueError(
                        f"Customer with email '{email}' already exists."
                    )

            if owner_id is not None:

                owner = session.get(
                    User,
                    owner_id,
                )

                if not owner:
                    raise ValueError(
                        f"User with id {owner_id} does not exist."
                    )

            now = utc_now()

            customer = Customer(
                name=name,
                company_name=_normalize_optional(company_name),
                email=email,
                phone=_normalize_optional(phone),
                address=_normalize_optional(address),
                city=_normalize_optional(city),
                country=_normalize_optional(country),
                region=_normalize_optional(region),
                industry=_normalize_optional(industry),
                notes=_normalize_optional(notes),
                owner_id=owner_id,
                created_at=now,
                updated_at=now,
            )
            
            session.add(customer)
            session.commit()
            session.refresh(customer)

            return customer

    def get_customer(
        self,
        email: str,
    ) -> Optional[Customer]:

        email = _normalize_email(email)

        if not email:
            return None

        with get_session() as session:

            statement = select(Customer).where(
                Customer.email == email
            )

            return session.exec(statement).first()

    def get_customer_by_id(
        self,
        customer_id: int,
    ) -> Optional[Customer]:

        if customer_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Customer,
                customer_id,
            )

    # ========================================================================
    # CONTACTS
    # ========================================================================

    def add_contact(
        self,
        customer_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        job_title: Optional[str] = None,
        is_primary: bool = False,
    ) -> Contact:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        first_name = _require_non_empty(
            first_name,
            "First name",
        )

        email = _normalize_email(email)

        with get_session() as session:

            customer = session.get(
                Customer,
                customer_id,
            )

            if not customer:
                raise ValueError(
                    f"Customer with id {customer_id} does not exist."
                )

            if email:

                existing_contact = session.exec(
                    select(Contact).where(
                        Contact.email == email
                    )
                ).first()

                if existing_contact:
                    raise ValueError(
                        f"Contact with email '{email}' already exists."
                    )

            # If this contact becomes primary, remove the existing
            # primary flag for this customer.
            if is_primary:
                
                existing_primary = session.exec(
                    select(Contact).where(
                        Contact.customer_id == customer_id,
                        Contact.is_primary == True,  # noqa: E712
                    )
                ).all()

                for existing in existing_primary:
                    existing.is_primary = False
                    existing.updated_at = utc_now()

            now = utc_now()

            contact = Contact(
                customer_id=customer_id,
                first_name=first_name,
                last_name=_normalize_optional(last_name),
                email=email,
                phone=_normalize_optional(phone),
                job_title=_normalize_optional(job_title),
                is_primary=is_primary,
                created_at=now,
                updated_at=now,
            )

            session.add(contact)
            session.commit()
            session.refresh(contact)

            return contact

    def get_contact(
        self,
        email: str,
    ) -> Optional[Contact]:

        email = _normalize_email(email)

        if not email:
            return None

        with get_session() as session:

            statement = select(Contact).where(
                Contact.email == email
            )

            return session.exec(statement).first()

    def get_contact_by_id(
        self,
        contact_id: int,
    ) -> Optional[Contact]:

        if contact_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Contact,
                contact_id,
            )

    def get_customer_contacts(
        self,
        customer_id: int,
    ) -> list[Contact]:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        with get_session() as session:

            statement = (
                select(Contact)
                .where(
                    Contact.customer_id == customer_id
                )
                .order_by(Contact.id)
            )

            return list(
                session.exec(statement).all()
            )

    # ========================================================================
    # PRODUCTS
    # ========================================================================

    def add_product(
        self,
        name: str,
        sku: str,
        description: Optional[str] = None,
        price: Decimal = Decimal("0.00"),
        cost: Decimal = Decimal("0.00"),
        stock_quantity: int = 0,
        is_active: bool = True,
    ) -> Product:

        name = _require_non_empty(
            name,
            "Product name",
        )

        sku = _require_non_empty(
            sku,
            "SKU",
        ).upper()

        _validate_non_negative(
            price,
            "Price",
        )

        _validate_non_negative(
            cost,
            "Cost",
        )

        if stock_quantity < 0:
            raise ValueError(
                "Stock quantity cannot be negative."
            )

        with get_session() as session:

            existing_product = session.exec(
                select(Product).where(
                    Product.sku == sku
                )
            ).first()

            if existing_product:
                raise ValueError(
                    f"Product with SKU '{sku}' already exists."
                )

            now = utc_now()

            product = Product(
                name=name,
                sku=sku,
                description=_normalize_optional(description),
                price=price,
                cost=cost,
                stock_quantity=stock_quantity,
                is_active=is_active,
                created_at=now,
                updated_at=now,
            )

            session.add(product)
            session.commit()
            session.refresh(product)

            return product

    def get_product(
        self,
        sku: str,
    ) -> Optional[Product]:

        sku = _normalize_optional(sku)

        if not sku:
            return None

        with get_session() as session:

            statement = select(Product).where(
                Product.sku == sku.upper()
            )

            return session.exec(statement).first()

    def get_product_by_id(
        self,
        product_id: int,
    ) -> Optional[Product]:

        if product_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Product,
                product_id,
            )

    # ========================================================================
    # LEADS
    # ========================================================================

    def add_lead(
        self,
        customer_id: Optional[int],
        contact_id: Optional[int],
        owner_id: Optional[int],
        title: str,
        source: Optional[str] = None,
        status: LeadStatus = LeadStatus.NEW,
        estimated_value: Decimal = Decimal("0.00"),
        notes: Optional[str] = None,
    ) -> Lead:

        title = _require_non_empty(
            title,
            "Lead title",
        )

        _validate_non_negative(
            estimated_value,
            "Estimated value",
        )

        with get_session() as session:

            customer = None
            contact = None

            if customer_id is not None:

                customer = session.get(
                    Customer,
                    customer_id,
                )

                if not customer:
                    raise ValueError(
                        f"Customer with id {customer_id} does not exist."
                    )

            if contact_id is not None:

                contact = session.get(
                    Contact,
                    contact_id,
                )

                if not contact:
                    raise ValueError(
                        f"Contact with id {contact_id} does not exist."
                    )

                # A contact cannot belong to a different customer.
                if (
                    customer_id is not None
                    and contact.customer_id != customer_id
                ):
                    raise ValueError(
                        "Contact does not belong to the supplied customer."
                    )

                # If customer was omitted, derive it from the contact.
                if customer_id is None:
                    customer_id = contact.customer_id

            if owner_id is not None:

                owner = session.get(
                    User,
                    owner_id,
                )

                if not owner:
                    raise ValueError(
                        f"User with id {owner_id} does not exist."
                    )

            now = utc_now()

            lead = Lead(
                customer_id=customer_id,
                contact_id=contact_id,
                owner_id=owner_id,
                title=title,
                source=_normalize_optional(source),
                status=status,
                estimated_value=estimated_value,
                notes=_normalize_optional(notes),
                created_at=now,
                updated_at=now,
            )

            session.add(lead)
            session.commit()
            session.refresh(lead)

            return lead

    def get_lead(
        self,
        contact_id: int,
    ) -> Optional[Lead]:

        _validate_positive(
            contact_id,
            "Contact ID",
        )

        with get_session() as session:

            statement = (
                select(Lead)
                .where(
                    Lead.contact_id == contact_id
                )
                .order_by(Lead.id.desc())
            )

            return session.exec(statement).first()

    def get_leads_by_customer(
        self,
        customer_id: int,
    ) -> list[Lead]:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        with get_session() as session:

            statement = (
                select(Lead)
                .where(
                    Lead.customer_id == customer_id
                )
                .order_by(Lead.id.desc())
            )

            return list(
                session.exec(statement).all()
            )

    def get_lead_by_id(
        self,
        lead_id: int,
    ) -> Optional[Lead]:

        if lead_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Lead,
                lead_id,
            )

    # ========================================================================
    # DEALS
    # ========================================================================

    def add_deal(
        self,
        customer_id: int,
        owner_id: Optional[int],
        title: str,
        amount: Decimal = Decimal("0.00"),
        probability: int = 0,
        stage: DealStage = DealStage.PROSPECTING,
        expected_close_date: Optional[date] = None,
        actual_close_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> Deal:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        title = _require_non_empty(
            title,
            "Deal title",
        )

        _validate_non_negative(
            amount,
            "Deal amount",
        )

        if not 0 <= probability <= 100:
            raise ValueError(
                "Probability must be between 0 and 100."
            )

        if (
            actual_close_date is not None
            and expected_close_date is not None
            and actual_close_date < expected_close_date
        ):
            raise ValueError(
                "Actual close date cannot be before expected close date."
            )

        with get_session() as session:

            customer = session.get(
                Customer,
                customer_id,
            )

            if not customer:
                raise ValueError(
                    f"Customer with id {customer_id} does not exist."
                )

            if owner_id is not None:

                owner = session.get(
                    User,
                    owner_id,
                )

                if not owner:
                    raise ValueError(
                        f"User with id {owner_id} does not exist."
                    )

            now = utc_now()

            deal = Deal(
                customer_id=customer_id,
                owner_id=owner_id,
                title=title,
                amount=amount,
                probability=probability,
                stage=stage,
                expected_close_date=expected_close_date,
                actual_close_date=actual_close_date,
                notes=_normalize_optional(notes),
                created_at=now,
                updated_at=now,
            )

            session.add(deal)
            session.commit()
            session.refresh(deal)

            return deal

    def get_deal_by_id(
        self,
        deal_id: int,
    ) -> Optional[Deal]:

        if deal_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Deal,
                deal_id,
            )

    def get_customer_deals(
        self,
        customer_id: int,
    ) -> list[Deal]:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        with get_session() as session:

            statement = (
                select(Deal)
                .where(
                    Deal.customer_id == customer_id
                )
                .order_by(Deal.id.desc())
            )

            return list(
                session.exec(statement).all()
            )

    # ========================================================================
    # DEAL PRODUCTS
    # ========================================================================

    def add_deal_product(
        self,
        deal_id: int,
        product_id: int,
        quantity: int,
        unit_price: Decimal,
        discount: Decimal = Decimal("0.00"),
    ) -> DealProduct:

        _validate_positive(
            deal_id,
            "Deal ID",
        )

        _validate_positive(
            product_id,
            "Product ID",
        )

        _validate_positive(
            quantity,
            "Quantity",
        )

        _validate_non_negative(
            unit_price,
            "Unit price",
        )

        _validate_non_negative(
            discount,
            "Discount",
        )

        _validate_percentage(
            discount,
            "Discount",
        )

        with get_session() as session:

            deal = session.get(
                Deal,
                deal_id,
            )

            if not deal:
                raise ValueError(
                    f"Deal with id {deal_id} does not exist."
                )

            product = session.get(
                Product,
                product_id,
            )

            if not product:
                raise ValueError(
                    f"Product with id {product_id} does not exist."
                )

            # Prevent accidental duplicate product lines.
            existing_line = session.exec(
                select(DealProduct).where(
                    DealProduct.deal_id == deal_id,
                    DealProduct.product_id == product_id,
                )
            ).first()

            if existing_line:
                raise ValueError(
                    "This product is already associated with "
                    f"deal {deal_id}."
                )

            subtotal = (
                unit_price * quantity
            )

            total = subtotal * (
                Decimal("1")
                - discount / Decimal("100")
            )

            deal_product = DealProduct(
                deal_id=deal_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                discount=discount,
                total=total,
            )

            session.add(deal_product)

            # Keep deal total synchronized.
            deal.amount = (
                deal.amount + total
            )
            deal.updated_at = utc_now()

            session.commit()
            session.refresh(deal_product)

            return deal_product

    def get_deal_products(
        self,
        deal_id: int,
    ) -> list[DealProduct]:

        _validate_positive(
            deal_id,
            "Deal ID",
        )

        with get_session() as session:

            statement = (
                select(DealProduct)
                .where(
                    DealProduct.deal_id == deal_id
                )
                .order_by(DealProduct.id)
            )

            return list(
                session.exec(statement).all()
            )

    # ========================================================================
    # SALES
    # ========================================================================

    def add_sale(
        self,
        customer_id: int,
        product_id: int,
        quantity: int,
        unit_price: Decimal,
        salesperson_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        discount: Decimal = Decimal("0.00"),
        sale_date: Optional[date] = None,
    ) -> Sale:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        _validate_positive(
            product_id,
            "Product ID",
        )

        _validate_positive(
            quantity,
            "Quantity",
        )

        _validate_non_negative(
            unit_price,
            "Unit price",
        )

        _validate_non_negative(
            discount,
            "Discount",
        )

        _validate_percentage(
            discount,
            "Discount",
        )

        with get_session() as session:

            customer = session.get(
                Customer,
                customer_id,
            )

            if not customer:
                raise ValueError(
                    f"Customer with id {customer_id} does not exist."
                )

            product = session.get(
                Product,
                product_id,
            )

            if not product:
                raise ValueError(
                    f"Product with id {product_id} does not exist."
                )

            if not product.is_active:
                raise ValueError(
                    f"Product '{product.name}' is not active."
                )

            if salesperson_id is not None:

                salesperson = session.get(
                    User,
                    salesperson_id,
                )

                if not salesperson:
                    raise ValueError(
                        f"User with id {salesperson_id} does not exist."
                    )

            if deal_id is not None:

                deal = session.get(
                    Deal,
                    deal_id,
                )

                if not deal:
                    raise ValueError(
                        f"Deal with id {deal_id} does not exist."
                    )

                # Prevent cross-customer sales/deal relationships.
                if deal.customer_id != customer_id:
                    raise ValueError(
                        "The supplied deal does not belong "
                        "to the supplied customer."
                    )

            if quantity > product.stock_quantity:
                raise ValueError(
                    "Not enough product stock."
                )

            subtotal = (
                unit_price * quantity
            )

            revenue = subtotal * (
                Decimal("1")
                - discount / Decimal("100")
            )

            now = utc_now()

            sale = Sale(
                customer_id=customer_id,
                salesperson_id=salesperson_id,
                deal_id=deal_id,
                product_id=product_id,
                sale_date=sale_date or date.today(),
                quantity=quantity,
                unit_price=unit_price,
                discount=discount,
                revenue=revenue,
                created_at=now,
            )

            # Reduce stock and create sale in the same transaction.
            product.stock_quantity -= quantity
            product.updated_at = now

            session.add(sale)
            session.commit()
            session.refresh(sale)

            return sale

    def get_sale_by_id(
        self,
        sale_id: int,
    ) -> Optional[Sale]:

        if sale_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Sale,
                sale_id,
            )

    def get_customer_sales(
        self,
        customer_id: int,
    ) -> list[Sale]:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        with get_session() as session:

            statement = (
                select(Sale)
                .where(
                    Sale.customer_id == customer_id
                )
                .order_by(
                    Sale.sale_date.desc(),
                    Sale.id.desc(),
                )
            )

            return list(
                session.exec(statement).all()
            )

    # ========================================================================
    # ACTIVITIES
    # ========================================================================

    def add_activity(
        self,
        subject: str,
        activity_type: ActivityType = ActivityType.NOTE,
        user_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        description: Optional[str] = None,
        activity_date: Optional[datetime] = None,
        completed: bool = False,
    ) -> Activity:

        subject = _require_non_empty(
            subject,
            "Activity subject",
        )

        with get_session() as session:

            customer = None
            contact = None

            if user_id is not None:

                user = session.get(
                    User,
                    user_id,
                )

                if not user:
                    raise ValueError(
                        f"User with id {user_id} does not exist."
                    )

            if customer_id is not None:

                customer = session.get(
                    Customer,
                    customer_id,
                )

                if not customer:
                    raise ValueError(
                        f"Customer with id {customer_id} does not exist."
                    )

            if contact_id is not None:

                contact = session.get(
                    Contact,
                    contact_id,
                )

                if not contact:
                    raise ValueError(
                        f"Contact with id {contact_id} does not exist."
                    )

                if (
                    customer_id is not None
                    and contact.customer_id != customer_id
                ):
                    raise ValueError(
                        "Contact does not belong to the supplied customer."
                    )

                if customer_id is None:
                    customer_id = contact.customer_id

            now = utc_now()

            activity = Activity(
                user_id=user_id,
                customer_id=customer_id,
                contact_id=contact_id,
                activity_type=activity_type,
                subject=subject,
                description=_normalize_optional(description),
                activity_date=activity_date or now,
                completed=completed,
                created_at=now,
            )

            session.add(activity)
            session.commit()
            session.refresh(activity)

            return activity

    def get_activity_by_id(
        self,
        activity_id: int,
    ) -> Optional[Activity]:

        if activity_id <= 0:
            return None

        with get_session() as session:
            return session.get(
                Activity,
                activity_id,
            )

    # ========================================================================
    # CUSTOMER FEEDBACK
    # ========================================================================

    def add_customer_feedback(
    self,
    customer_id: int,
    rating: FeedbackRating,
    subject: Optional[str] = None,
    comments: Optional[str] = None,
    submitted_at: Optional[datetime] = None,
    email_message_id: Optional[int] = None,
    ) -> CustomerFeedback:

      if customer_id is None:
        raise ValueError("Customer ID is required.")

      if not isinstance(rating, FeedbackRating):
        try:
            rating = FeedbackRating(rating)
        except ValueError as exc:
            raise ValueError(
                f"Invalid feedback rating: {rating}"
            ) from exc

      with get_session() as session:

        # Verify customer exists
        customer = session.get(Customer, customer_id)

        if not customer:
            raise ValueError(
                f"Customer with id {customer_id} does not exist."
            )

        # If feedback came from an email,
        # verify that the email exists.
        if email_message_id is not None:
            email_message = session.get(
                EmailMessage,
                email_message_id,
            )

            if not email_message:
                raise ValueError(
                    f"EmailMessage with id "
                    f"{email_message_id} does not exist."
                )

        feedback = CustomerFeedback(
            customer_id=customer_id,
            email_message_id=email_message_id,
            rating=rating,
            subject=_normalize_optional(subject),
            comments=_normalize_optional(comments),
            submitted_at=submitted_at or utc_now(),
        )

        session.add(feedback)
        session.commit()
        session.refresh(feedback)

        return feedback

    def get_customer_feedback(
        self,
        customer_id: int,
    ) -> list[CustomerFeedback]:

        _validate_positive(
            customer_id,
            "Customer ID",
        )

        with get_session() as session:

            statement = (
                select(CustomerFeedback)
                .where(
                    CustomerFeedback.customer_id == customer_id
                )
                .order_by(
                    CustomerFeedback.submitted_at.desc()
                )
            )

            return list(
                session.exec(statement).all()
            )
        
    def get_feedback_by_email_id(
    self,
    email_message_id: int,
    ) -> Optional[CustomerFeedback]:

     with get_session() as session:
        statement = select(CustomerFeedback).where(
            CustomerFeedback.email_message_id == email_message_id
        )

        return session.exec(statement).first()
    # ========================================================================
    # GENERAL HELPERS
    # ========================================================================

    def delete_user(
        self,
        user_id: int,
    ) -> bool:

        if user_id <= 0:
            return False

        with get_session() as session:

            user = session.get(
                User,
                user_id,
            )

            if not user:
                return False

            session.delete(user)
            session.commit()

            return True

    def delete_product(
        self,
        product_id: int,
    ) -> bool:

        if product_id <= 0:
            return False

        with get_session() as session:

            product = session.get(
                Product,
                product_id,
            )

            if not product:
                return False

            session.delete(product)
            session.commit()

            return True
        
    def get_email_by_gmail_id(self,gmail_message_id: str) -> Optional[EmailMessage]:

        gmail_message_id = _require_non_empty(
        gmail_message_id,
        "Gmail message ID",
    )

        with get_session() as session:

            statement = select(EmailMessage).where(
                    EmailMessage.gmail_message_id == gmail_message_id
        )

            return session.exec(statement).first()
    
    
    def add_email_message(self,gmail_message_id: str,thread_id: Optional[str],customer_id: Optional[int],sender_name: Optional[str],sender_email: str,recipient: Optional[str],cc: Optional[str],subject: Optional[str],body: str,received_at: Optional[datetime],labels: Optional[str] = None) -> EmailMessage:

        gmail_message_id = _require_non_empty(
          gmail_message_id,
          "Gmail message ID",
        )

        sender_email = _normalize_email(sender_email )

        if not sender_email:
             raise ValueError(
              "Sender email cannot be empty.")

        body = _require_non_empty(
           body,
           "Email body",
        )

        with get_session() as session:
 
        # --------------------------------------------------
        # IDEMPOTENCY
        # --------------------------------------------------

           existing = session.exec(
            select(EmailMessage).where(
                EmailMessage.gmail_message_id == gmail_message_id)
            ).first()

           if existing:
              return existing

        # --------------------------------------------------
        # VALIDATE CUSTOMER
        # --------------------------------------------------

        if customer_id is not None:

            customer = session.get(
                Customer,
                customer_id,
            )

            if not customer:
                raise ValueError(
                    f"Customer with id {customer_id} "
                    "does not exist."
                )

        # --------------------------------------------------
        # CREATE EMAIL
        # --------------------------------------------------

        email = EmailMessage(
            gmail_message_id=gmail_message_id,
            thread_id=_normalize_optional(thread_id),
            customer_id=customer_id,
            sender_name=_normalize_optional(sender_name),
            sender_email=sender_email,
            recipient=_normalize_optional(recipient),
            cc=_normalize_optional(cc),
            subject=_normalize_optional(subject),
            body=body,
            received_at=received_at,
            labels=_normalize_optional(labels),
            created_at=utc_now(),
        )

        session.add(email)

        session.commit()

        session.refresh(email)

        return email
    
    def get_recent_customer_feedback(
    self,
    limit: int = 50,
    ) -> list[CustomerFeedback]:

      if limit < 1:
        raise ValueError("Limit must be greater than 0.")

      with get_session() as session:
        statement = (
            select(CustomerFeedback)
            .order_by(
                CustomerFeedback.submitted_at.desc()
            )
            .limit(limit)
        )

        return list(
            session.exec(statement).all()
        )