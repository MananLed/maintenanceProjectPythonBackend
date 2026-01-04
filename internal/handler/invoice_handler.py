from fastapi import APIRouter, HTTPException, Query, Request, Depends
from http import HTTPStatus
from typing import Annotated
from internal.dto.invoice import InvoiceInput
from internal.models.user import UserRole
from internal.utils.jwt import verify_jwt
from internal.service import invoice_service_instance
from internal.response.response import Response
from internal.constants.constants import SERVER_ERROR

invoice_router = APIRouter(dependencies=[Depends(verify_jwt)])


@invoice_router.post("/invoices/issue")
async def issue_invoice(invoice_input: InvoiceInput, request: Request):
    claims = request.state.user

    if claims.get("role") != UserRole.ROLEADMIN and claims.get("role") != UserRole.ROLEOFFICER:
        return Response.error_response("Unauthorized access", HTTPStatus.UNAUTHORIZED)
    
    try:
        await invoice_service_instance.issue_invoice(invoice_input)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Invoice issued successfully", HTTPStatus.CREATED)


@invoice_router.get("/invoices/month-year")
async def get_invoices_month_year(year: Annotated[int, Query(ge=0)], month: Annotated[int | None, Query(gt=0, lt=13)] = None):
    try:
        invoices = await invoice_service_instance.get_all_invoices_by_month_and_year(year, month)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(invoices, "Invoices fetched successfully", HTTPStatus.OK)
