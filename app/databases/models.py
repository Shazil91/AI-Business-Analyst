from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import timezone


# ============================================================
# Enums
# ============================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALES = "sales"
    SUPPORT = "support"


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    LOST = "lost"
    CONVERTED = "converted"


class DealStage(str, Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"


class FeedbackRating(str, Enum):
    VERY_BAD = "very_bad"
    BAD = "bad"
    NEUTRAL = "neutral"
    GOOD = "good"
    VERY_GOOD = "very_good"

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# ============================================================
# Users
# ============================================================

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: UserRole = Field(default=UserRole.SALES)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customers: list["Customer"] = Relationship(back_populates="owner")
    leads: list["Lead"] = Relationship(back_populates="owner")
    deals: list["Deal"] = Relationship(back_populates="owner")
    activities: list["Activity"] = Relationship(back_populates="user")
    sales: list["Sale"] = Relationship(back_populates="salesperson")


# ============================================================
# Customers
# ============================================================
class Customer(SQLModel, table=True):

    __tablename__ = "customers"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str

    company_name: Optional[str] = None

    email: Optional[str] = Field(
        default=None,
        index=True
    )

    phone: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = Field(
        default=None,
        index=True
    )

    industry: Optional[str] = None
    notes: Optional[str] = None

    owner_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    owner: Optional["User"] = Relationship(
        back_populates="customers"
    )

    contacts: list["Contact"] = Relationship(
        back_populates="customer"
    )

    leads: list["Lead"] = Relationship(
        back_populates="customer"
    )

    deals: list["Deal"] = Relationship(
        back_populates="customer"
    )

    sales: list["Sale"] = Relationship(
        back_populates="customer"
    )

    activities: list["Activity"] = Relationship(
        back_populates="customer"
    )

    feedback: list["CustomerFeedback"] = Relationship(
        back_populates="customer"
    )

    emails: list["EmailMessage"] = Relationship(
        back_populates="customer"
    )

# ============================================================
# Contacts
# ============================================================

class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: int = Field(
        foreign_key="customers.id",
        index=True
    )

    first_name: str
    last_name: Optional[str] = None

    email: Optional[str] = Field(default=None, index=True)
    phone: Optional[str] = None

    job_title: Optional[str] = None
    is_primary: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship(
        back_populates="contacts"
    )

    leads: list["Lead"] = Relationship(back_populates="contact")
    activities: list["Activity"] = Relationship(back_populates="contact")


# ============================================================
# Products
# ============================================================

class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    sku: str = Field(unique=True, index=True)

    description: Optional[str] = None

    price: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    cost: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    stock_quantity: int = Field(default=0)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    deal_products: list["DealProduct"] = Relationship(
        back_populates="product"
    )

    sales: list["Sale"] = Relationship(back_populates="product")


# ============================================================
# Leads
# ============================================================

class Lead(SQLModel, table=True):
    __tablename__ = "leads"

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: Optional[int] = Field(
        default=None,
        foreign_key="customers.id",
        index=True
    )

    contact_id: Optional[int] = Field(
        default=None,
        foreign_key="contacts.id",
        index=True
    )

    owner_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True
    )

    title: str
    source: Optional[str] = None

    status: LeadStatus = Field(default=LeadStatus.NEW)

    estimated_value: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship(
        back_populates="leads"
    )

    contact: Optional["Contact"] = Relationship(
        back_populates="leads"
    )

    owner: Optional["User"] = Relationship(
        back_populates="leads"
    )


# ===========================================================
# Deals
# ===========================================================

class Deal(SQLModel, table=True):
    __tablename__ = "deals"

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: int = Field(
        foreign_key="customers.id",
        index=True
    )

    owner_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True
    )

    title: str

    stage: DealStage = Field(
        default=DealStage.PROSPECTING,
        index=True
    )

    amount: Decimal = Field(
        default=0,
        max_digits=14,
        decimal_places=2
    )

    probability: int = Field(default=0, ge=0, le=100)

    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None

    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship(
        back_populates="deals"
    )

    owner: Optional["User"] = Relationship(
        back_populates="deals"
    )

    products: list["DealProduct"] = Relationship(
        back_populates="deal"
    )

    sales: list["Sale"] = Relationship(back_populates="deal")


# ===========================================================
# Deal Products
# ===========================================================

class DealProduct(SQLModel, table=True):
    __tablename__ = "deal_products"

    id: Optional[int] = Field(default=None, primary_key=True)

    deal_id: int = Field(
        foreign_key="deals.id",
        index=True
    )

    product_id: int = Field(
        foreign_key="products.id",
        index=True
    )

    quantity: int = Field(default=1, ge=1)

    unit_price: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    discount: Decimal = Field(
        default=0,
        max_digits=5,
        decimal_places=2
    )

    total: Decimal = Field(
        default=0,
        max_digits=14,
        decimal_places=2
    )

    deal: Optional["Deal"] = Relationship(
      
        back_populates="products"
    )

    product: Optional["Product"] = Relationship(
        back_populates="deal_products"
    )


# ============================================================
# Sales
# ============================================================

class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: int = Field(
        foreign_key="customers.id",
        index=True
    )

    salesperson_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True
    )

    deal_id: Optional[int] = Field(
        default=None,
        foreign_key="deals.id",
        index=True
    )

    product_id: int = Field(
        foreign_key="products.id",
        index=True
    )

    sale_date: date = Field(default_factory=date.today)

    quantity: int = Field(default=1, ge=1)

    unit_price: Decimal = Field(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    discount: Decimal = Field(
        default=0,
        max_digits=5,
        decimal_places=2
    )

    revenue: Decimal = Field(
        default=0,
        max_digits=14,
        decimal_places=2
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship(
        back_populates="sales"
    )

    salesperson: Optional["User"] = Relationship(
        back_populates="sales"
    )

    deal: Optional["Deal"] = Relationship(
        back_populates="sales"
    )

    product: Optional["Product"] = Relationship(
        back_populates="sales"
    )


# ============================================================
# Activities
# ============================================================

class Activity(SQLModel, table=True):
    __tablename__ = "activities"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True
    )

    customer_id: Optional[int] = Field(
        default=None,
        foreign_key="customers.id",
        index=True
    )

    contact_id: Optional[int] = Field(
        default=None,
        foreign_key="contacts.id",
        index=True
    )

    activity_type: ActivityType = Field(
        default=ActivityType.NOTE
    )

    subject: str
    description: Optional[str] = None

    activity_date: datetime = Field(
        default_factory=datetime.utcnow
    )

    completed: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(
        back_populates="activities"
    )

    customer: Optional["Customer"] = Relationship(
        back_populates="activities"
    )

    contact: Optional["Contact"] = Relationship(
        back_populates="activities"
    )


# ============================================================
# Customer Feedback
# ============================================================
class CustomerFeedback(SQLModel, table=True):
    __tablename__ = "customer_feedback"

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: int = Field(
        foreign_key="customers.id",
        index=True,
    )

    email_message_id: Optional[int] = Field(
        default=None,
        foreign_key="email_messages.id",
        index=True,
    )

    rating: FeedbackRating

    subject: Optional[str] = None

    comments: Optional[str] = None

    submitted_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    customer: Optional["Customer"] = Relationship(
        back_populates="feedback"
    )

class EmailMessage(SQLModel, table=True):
    __tablename__ = "email_messages"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    gmail_message_id: str = Field(
        index=True,
        unique=True,
    )

    thread_id: Optional[str] = Field(
        default=None,
        index=True,
    )

    customer_id: Optional[int] = Field(
        default=None,
        foreign_key="customers.id",
        index=True,
    )

    sender_name: Optional[str] = None
    sender_email: str = Field(index=True)

    recipient: Optional[str] = None
    cc: Optional[str] = None
    subject: Optional[str] = None

    body: str

    received_at: Optional[datetime] = None

    labels: Optional[str] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    customer: Optional["Customer"] = Relationship(
        back_populates="emails"
    )