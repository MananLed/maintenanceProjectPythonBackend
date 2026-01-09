from typing import List
from internal.models.invoice import Invoice
from internal.errors.base_exception import AppException
from internal.constants.constants import *
import uuid
import asyncio

class InvoiceRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    async def issue_invoice(self, invoice: Invoice):
        invoice_id = str(invoice.id)

        statement = f"INSERT INTO {self.table_name} VALUE {{'PK': ?, 'SK': ?, 'id': ?, 'amount': ?, 'month': ?, 'year': ?}}"

        parameters = [
            {"S": "INVOICES"},
            {"S": f"{invoice.year}#{invoice.month}#{invoice_id}"},
            {"S": invoice_id},
            {"N": f"{invoice.amount:.2f}"},
            {"S": str(invoice.month)},
            {"N": str(invoice.year)} 
        ]

        try:
            await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=statement,
                Parameters=parameters
            )
        except:
            raise AppException(INVOICE_001)

    async def get_all_invoices_by_month_and_year(self, year: int, month: int | None = None):
        if month is not None:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                    Parameters=[{"S": "INVOICES"}, {"S": (str(year) + "#" + str(month))}]
                )
            except:
                raise AppException(INVOICE_002)
        elif year == 0:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                    Parameters=[{"S": "INVOICES"}]
                )
            except:
                raise AppException(INVOICE_002)
        else:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                    Parameters=[{"S": "INVOICES"}, {"S": str(year)}]
                )
            except:
                raise AppException(INVOICE_002)
            
        items = response["Items"]

        invoices: List[Invoice] = []

        for item in items:
            invoice_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            invoice: Invoice = Invoice.model_construct(amount = float(invoice_details.get("amount")), month = int(invoice_details.get("month")), 
                                    year = int(invoice_details.get("year")), id = uuid.UUID(invoice_details.get("id")))
            
            invoices.append(invoice)

        return invoices