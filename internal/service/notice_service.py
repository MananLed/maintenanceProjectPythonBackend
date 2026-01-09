from datetime import datetime
from internal.dto.notice import NoticeInput
from internal.models.notice import Notice
from internal.repository import notice_repository_instance

class NoticeService:
    def __init__(self):
        self.notice_repository = notice_repository_instance

    async def issue_notice(self, notice_input: NoticeInput):

        now = datetime.utcnow()

        notice: Notice = Notice.model_construct(**notice_input.model_dump(), date_issued=now, month=now.month, year=now.year) 

        await self.notice_repository.issue_notice(notice)

    async def get_all_notices(self):

        notices = await self.notice_repository.get_all_notices()
        
        return notices
    
    async def get_all_notices_by_month_and_year(self, year: int, month: int | None = None):

        notices = await self.notice_repository.get_all_notices_by_month_and_year(year, month)
        
        return notices