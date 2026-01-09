from fastapi import APIRouter, Query, Depends
from http import HTTPStatus
from typing import Annotated
from internal.dto.invoice import InvoiceInput
from internal.models.user import UserRole
from internal.response.response import Response
from internal.utils.jwt import verify_jwt
from internal.dependencies.authorization import require_roles
from internal.service import invoice_service_instance
from internal.constants.constants import INVOICE_EMAIL_TOPIC_ARN
from internal.dependencies.dependencies import sns_client

invoice_router = APIRouter(dependencies=[Depends(verify_jwt)])


@invoice_router.post("/invoices/issue", dependencies=[Depends(require_roles(UserRole.ROLEADMIN, UserRole.ROLEOFFICER))])
async def issue_invoice(invoice_input: InvoiceInput):

    await invoice_service_instance.issue_invoice(invoice_input)
    sns_client.publish(
        TopicArn=INVOICE_EMAIL_TOPIC_ARN,
        Message=f"Bill of Rs. {invoice_input.amount:.2f} is issued, please check your dashboard."
    )
    
    return Response.success_response(None, "Invoice issued successfully", HTTPStatus.CREATED)


@invoice_router.get("/invoices/month-year")
async def get_invoices_month_year(year: Annotated[int, Query(ge=0)], month: Annotated[int | None, Query(gt=0, lt=13)] = None):

    invoices = await invoice_service_instance.get_all_invoices_by_month_and_year(year, month)
    
    return Response.success_response(invoices, "Invoices fetched successfully", HTTPStatus.OK)
