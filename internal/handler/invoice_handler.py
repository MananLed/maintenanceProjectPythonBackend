from fastapi import APIRouter
from models.invoice import InvoiceInput

invoice_router = APIRouter()

@invoice_router.post("/invoices/issue")
def issue_invoice(invoice_input: InvoiceInput):
    pass 

@invoice_router.get("/invoices/month-year")
def get_invoices_month_year():
    pass