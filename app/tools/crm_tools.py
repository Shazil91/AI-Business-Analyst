from typing import Optional

from app.databases.memory import CompanyData


class CRMTools:

    def __init__(self):
        self.company_data = CompanyData()

    # =====================================================
    # CUSTOMER
    # =====================================================

    def get_customer(
        self,
        customer_id: Optional[int] = None,
        email: Optional[str] = None,
    ) -> dict:

        if customer_id is None and email is None:
            return {
                "success": False,
                "error": "Provide either customer_id or email."
            }

        if customer_id is not None:

            customer = self.company_data.get_customer_by_id(
                customer_id
            )

        else:

            customer = self.company_data.get_customer(
                email
            )

        if not customer:

            return {
                "success": False,
                "error": "Customer not found."
            }

        return {
            "success": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "company_name": customer.company_name,
                "email": customer.email,
                "phone": customer.phone,
                "city": customer.city,
                "country": customer.country,
                "industry": customer.industry,
                "notes": customer.notes,
                "owner_id": customer.owner_id,
                "created_at": customer.created_at.isoformat()
                if customer.created_at else None,
            }
        }

    # =====================================================
    # CUSTOMER CONTACTS
    # =====================================================

    def get_customer_contacts(
        self,
        customer_id: int,
    ) -> dict:

        contacts = self.company_data.get_customer_contacts(
            customer_id
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "contacts": [
                {
                    "id": contact.id,
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "job_title": contact.job_title,
                    "is_primary": contact.is_primary,
                }
                for contact in contacts
            ]
        }

    # =====================================================
    # LEADS
    # =====================================================

    def get_customer_leads(
        self,
        customer_id: int,
    ) -> dict:

        leads = self.company_data.get_leads_by_customer(
            customer_id
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "leads": [
                {
                    "id": lead.id,
                    "title": lead.title,
                    "source": lead.source,
                    "status": lead.status.value
                    if lead.status else None,
                    "estimated_value": float(
                        lead.estimated_value
                    ),
                    "notes": lead.notes,
                    "owner_id": lead.owner_id,
                    "created_at": lead.created_at.isoformat()
                    if lead.created_at else None,
                }
                for lead in leads
            ]
        }

    # =====================================================
    # DEALS
    # =====================================================

    def get_customer_deals(
        self,
        customer_id: int,
    ) -> dict:

        deals = self.company_data.get_customer_deals(
            customer_id
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "deals": [
                {
                    "id": deal.id,
                    "title": deal.title,
                    "stage": deal.stage.value
                    if deal.stage else None,
                    "amount": float(deal.amount),
                    "probability": deal.probability,
                    "expected_close_date":
                        deal.expected_close_date.isoformat()
                        if deal.expected_close_date
                        else None,
                    "actual_close_date":
                        deal.actual_close_date.isoformat()
                        if deal.actual_close_date
                        else None,
                    "owner_id": deal.owner_id,
                    "notes": deal.notes,
                }
                for deal in deals
            ]
        }

    # =====================================================
    # SALES
    # =====================================================

    def get_customer_sales(
        self,
        customer_id: int,
    ) -> dict:

        sales = self.company_data.get_customer_sales(
            customer_id
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "sales": [
                {
                    "id": sale.id,
                    "product_id": sale.product_id,
                    "deal_id": sale.deal_id,
                    "salesperson_id": sale.salesperson_id,
                    "sale_date": sale.sale_date.isoformat(),
                    "quantity": sale.quantity,
                    "unit_price": float(
                        sale.unit_price
                    ),
                    "discount": float(
                        sale.discount
                    ),
                    "revenue": float(
                        sale.revenue
                    ),
                }
                for sale in sales
            ]
        }

    # =====================================================
    # CUSTOMER FEEDBACK
    # =====================================================

    def get_customer_feedback(
        self,
        customer_id: int,
    ) -> dict:

        feedback = self.company_data.get_customer_feedback(
            customer_id
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "feedback": [
                {
                    "id": item.id,
                    "rating": item.rating.value
                    if item.rating else None,
                    "subject": item.subject,
                    "comments": item.comments,
                    "submitted_at":
                        item.submitted_at.isoformat()
                        if item.submitted_at
                        else None,
                }
                for item in feedback
            ]
        }