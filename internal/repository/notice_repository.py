from fastapi import HTTPException, status
from datetime import datetime
from typing import List
from internal.models.notice import Notice
import uuid
import asyncio


class NoticeRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    
    async def get_all_notices(self):
        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                Parameters=[{"S": "NOTICES"}]
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        items = response["Items"]

        notices: List[Notice] = []

        date_format = "%Y-%m-%d %H:%M:%S.%f"

        for item in items:
            notice_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            notice_date_issued = datetime.strptime(notice_details.get("date_issued"), date_format)

            notice: Notice = Notice(notice_date_issued, notice_details.get("content"), int(notice_details.get("month")), 
                                    notice_details.get("year"), uuid.UUID(notice_details.get("id")))
            
            notices.append(notice)

        return notices
    
    async def get_all_notices_by_month_and_year(self, year:int, month: int | None = None):
        if month is not None:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                    Parameters=[{"S": "NOTICES"}, {"S": (str(year) + "#" + str(month))}]
                )
            except:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            try:
                response = await asyncio.to_thread(
                    self.dynamodb.execute_statement,
                    Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                    Parameters=[{"S": "NOTICES"}, {"S": str(year)}]
                )
            except:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        
        items = response["Items"]

        notices: List[Notice] = []

        date_format = "%Y-%m-%d %H:%M:%S.%f"

        for item in items:
            notice_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            notice_date_issued = datetime.strptime(notice_details.get("date_issued"), date_format)

            notice: Notice = Notice(notice_date_issued, notice_details.get("content"), int(notice_details.get("month")), 
                                    notice_details.get("year"), uuid.UUID(notice_details.get("id")))
            
            notices.append(notice)

        return notices