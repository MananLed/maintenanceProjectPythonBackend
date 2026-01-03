class InvoiceRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    def get_all_invoices_by_month_and_year(self, year: int, month: int | None = None):
        pass