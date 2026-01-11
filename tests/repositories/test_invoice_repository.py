import pytest
import uuid
from unittest.mock import MagicMock
from internal.repository.invoice_repository import InvoiceRepository
from internal.models.invoice import Invoice
from internal.errors.base_exception import AppException
from internal.constants.constants import *


@pytest.fixture
def invoice():
    return Invoice.model_construct(
        id=str(uuid.uuid4()),
        amount=1234.50,
        month=9,
        year=2025,
    )

@pytest.mark.asyncio
async def test_issue_invoice_success(invoice):
    dynamodb = MagicMock()

    repo = InvoiceRepository(
        ddb_connection=dynamodb,
        table_name="InvoiceTable",
        deserializer=MagicMock,
    )

    await repo.issue_invoice(invoice)

    dynamodb.execute_statement.assert_called_once()

    kwargs = dynamodb.execute_statement.call_args.kwargs

    assert "Statement" in kwargs
    assert "Parameters" in kwargs

    params = kwargs["Parameters"]

    assert params[0]["S"] == "INVOICES"
    assert params[2]["S"] == invoice.id
    assert params[3]["N"] == f"{invoice.amount:.2f}"
    assert params[4]["S"] == str(invoice.month)
    assert params[5]["N"] == str(invoice.year)


@pytest.mark.asyncio
async def test_issue_invoice_db_exception(invoice):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DynamoDB down")

    repo = InvoiceRepository(
        ddb_connection=dynamodb,
        table_name="InvoiceTable",
        deserializer=MagicMock,
    )

    with pytest.raises(AppException) as exc:
        await repo.issue_invoice(invoice)

    assert exc.value.error_code == INVOICE_001
    assert exc.value.status_code == 500

@pytest.fixture
def dynamo_invoice_item():
    return {
        "id": {"S": str(uuid.uuid4())},
        "amount": {"N": "1500.50"},
        "month": {"S": "9"},
        "year": {"N": "2025"},
    }

@pytest.fixture
def fake_deserializer():
    class FakeDeserializer:
        def deserialize(self, value):
            return list(value.values())[0]
    return FakeDeserializer

@pytest.mark.asyncio
async def test_get_invoices_by_year_and_month(dynamo_invoice_item, fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {
        "Items": [dynamo_invoice_item]
    }

    repo = InvoiceRepository(
        ddb_connection=dynamodb,
        table_name="InvoiceTable",
        deserializer=fake_deserializer,
    )

    invoices = await repo.get_all_invoices_by_month_and_year(2025, 9)

    dynamodb.execute_statement.assert_called_once()

    assert len(invoices) == 1
    assert invoices[0].amount == 1500.50
    assert invoices[0].month == 9
    assert invoices[0].year == 2025

@pytest.mark.asyncio
async def test_get_invoices_by_year_only(dynamo_invoice_item, fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {
        "Items": [dynamo_invoice_item]
    }

    repo = InvoiceRepository(
        ddb_connection=dynamodb,
        table_name="InvoiceTable",
        deserializer=fake_deserializer,
    )

    invoices = await repo.get_all_invoices_by_month_and_year(2025)

    assert len(invoices) == 1

@pytest.mark.asyncio
async def test_get_all_invoices_year_zero(dynamo_invoice_item, fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {
        "Items": [dynamo_invoice_item, dynamo_invoice_item]
    }

    repo = InvoiceRepository(
        ddb_connection=dynamodb,
        table_name="InvoiceTable",
        deserializer=fake_deserializer,
    )

    invoices = await repo.get_all_invoices_by_month_and_year(0)

    assert len(invoices) == 2

@pytest.mark.asyncio
async def test_get_invoices_db_exception(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DynamoDB down")

    repo = InvoiceRepository(
        ddb_connection=dynamodb,
        table_name="InvoiceTable",
        deserializer=fake_deserializer,
    )

    with pytest.raises(AppException) as exc:
        await repo.get_all_invoices_by_month_and_year(2025, 9)

    assert exc.value.error_code == INVOICE_002
    assert exc.value.status_code == 500
