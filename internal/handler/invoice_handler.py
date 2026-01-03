from fastapi import APIRouter, HTTPException, Query
from http import HTTPStatus
from typing import Annotated
from internal.dto.invoice import InvoiceInput
from internal.service import invoice_service_instance
from internal.response.response import Response
from internal.constants.constants import SERVER_ERROR

invoice_router = APIRouter()


@invoice_router.post("/invoices/issue")
def issue_invoice(invoice_input: InvoiceInput):
    pass


@invoice_router.get("/invoices/month-year")
def get_invoices_month_year(year: Annotated[int, Query(ge=0)], month: Annotated[int | None, Query(gt=0, lt=13)] = None):
    try:
        invoices = invoice_service_instance.get_all_invoices_by_month_and_year(year, month)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(invoices, "Invoices fetched successfully", HTTPStatus.OK)
