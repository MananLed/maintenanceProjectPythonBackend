from fastapi import HTTPException
from datetime import datetime
from internal.dto.invoice import InvoiceInput
from internal.models.invoice import Invoice
from internal.repository import invoice_repository_instance

class InvoiceService:
    def __init__(self):
        self.invoice_repository = invoice_repository_instance

    async def issue_invoice(self, invoice_input: InvoiceInput):
        now = datetime.utcnow()

        invoice = Invoice.model_construct(
            **invoice_input.model_dump(),
            month = now.month, 
            year = now.year,
        )

        try:
            await self.invoice_repository.issue_invoice(invoice)
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception

    async def get_all_invoices_by_month_and_year(self, year: int, month: int | None = None):
        try:
            invoices = await self.invoice_repository.get_all_invoices_by_month_and_year(year, month)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception
        
        return invoices