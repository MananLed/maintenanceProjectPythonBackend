from fastapi import HTTPException
from datetime import datetime
from internal.dto.notice import NoticeInput
from internal.models.notice import Notice
from internal.repository import notice_repository_instance

class NoticeService:
    def __init__(self):
        self.notice_repository = notice_repository_instance

    async def issue_notice(self, notice_input: NoticeInput):

        now = datetime.utcnow()

        notice: Notice = Notice(**notice_input.model_dump(), date_issued=now, month=now.month, year=now.year)

        try:
            await self.notice_repository.issue_notice(notice)
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception

    async def get_all_notices(self):
        try:
            notices = await self.notice_repository.get_all_notices()
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception
        
        return notices
    
    async def get_all_notices_by_month_and_year(self, year: int, month: int | None = None):
        try:
            notices = await self.notice_repository.get_all_notices_by_month_and_year(year, month)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception
        
        return notices