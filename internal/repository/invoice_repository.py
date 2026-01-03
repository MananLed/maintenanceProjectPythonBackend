from fastapi import HTTPException, status
from typing import List
from internal.models.invoice import Invoice
import uuid
import asyncio

class InvoiceRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    async def get_all_invoices_by_month_and_year(self, year: int, month: int | None = None):
        if month is not None:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                    Parameters=[{"S": "INVOICES"}, {"S": (str(year) + "#" + str(month))}]
                )
            except:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        elif year == 0:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                    Parameters=[{"S": "INVOICES"}]
                )
            except:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                    Parameters=[{"S": "INVOICES"}, {"S": str(year)}]
                )
            except:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
            
        items = response["Items"]

        invoices: List[Invoice] = []

        for item in items:
            invoice_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            invoice: Invoice = Invoice(invoice_details.get("amount"), int(invoice_details.get("month")), 
                                    invoice_details.get("year"), uuid.UUID(invoice_details.get("id")))
            
            invoices.append(invoice)

        return invoices