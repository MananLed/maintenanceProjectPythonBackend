from fastapi import HTTPException
from internal.repository import invoice_repository_instance

class InvoiceService:
    def __init__(self):
        self.invoice_repository = invoice_repository_instance

    def get_all_invoices_by_month_and_year(self, year: int, month: int | None = None):
        try:
            notices = self.invoice_repository.get_all_invoices_by_month_and_year(year, month)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception
        
        return notices