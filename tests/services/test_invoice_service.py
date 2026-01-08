import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from internal.service.invoice_service import InvoiceService
from internal.models.invoice import Invoice
from internal.dto.invoice import InvoiceInput


@pytest.mark.asyncio
async def test_issue_invoice_success(mocker):
    service = InvoiceService()

    invoice_input = InvoiceInput(amount=100.0)

    mocker.patch(
        "internal.service.invoice_service.invoice_repository_instance.issue_invoice",
        new_callable=AsyncMock,
        return_value=None
    )

    await service.issue_invoice(invoice_input)

    service.invoice_repository.issue_invoice.assert_awaited_once()
    
@pytest.mark.asyncio
async def test_issue_invoice_http_exception(mocker):
    service = InvoiceService()
    invoice_input = InvoiceInput(amount=100.0)

    mocker.patch(
        "internal.service.invoice_service.invoice_repository_instance.issue_invoice",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=400, detail="Bad request")
    )

    with pytest.raises(HTTPException) as exc:
        await service.issue_invoice(invoice_input)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad request"

@pytest.mark.asyncio
async def test_issue_invoice_generic_exception(mocker):
    service = InvoiceService()
    invoice_input = InvoiceInput(amount=100.0)

    mocker.patch(
        "internal.service.invoice_service.invoice_repository_instance.issue_invoice",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )

    with pytest.raises(Exception) as exc:
        await service.issue_invoice(invoice_input)

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_get_all_invoices_by_month_and_year_success(mocker):
    service = InvoiceService()
    year, month = 2025, 5

    fake_invoices = [
        Invoice.model_construct(id="1", amount=100.0, month=month, year=year),
        Invoice.model_construct(id="2", amount=200.0, month=month, year=year),
    ]

    mocker.patch(
        "internal.service.invoice_service.invoice_repository_instance.get_all_invoices_by_month_and_year",
        new_callable=AsyncMock,
        return_value=fake_invoices
    )

    invoices = await service.get_all_invoices_by_month_and_year(year, month)
    assert invoices == fake_invoices
    assert len(invoices) == 2
    assert all(isinstance(inv, Invoice) for inv in invoices)

@pytest.mark.asyncio
async def test_get_all_invoices_by_month_and_year_http_exception(mocker):
    service = InvoiceService()
    year, month = 2025, 5

    mocker.patch(
        "internal.service.invoice_service.invoice_repository_instance.get_all_invoices_by_month_and_year",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=400, detail="Bad request")
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_all_invoices_by_month_and_year(year, month)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad request"

@pytest.mark.asyncio
async def test_get_all_invoices_by_month_and_year_generic_exception(mocker):
    service = InvoiceService()
    year, month = 2025, 5

    mocker.patch(
        "internal.service.invoice_service.invoice_repository_instance.get_all_invoices_by_month_and_year",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )

    with pytest.raises(Exception) as exc:
        await service.get_all_invoices_by_month_and_year(year, month)

    assert str(exc.value) == "DB down"
