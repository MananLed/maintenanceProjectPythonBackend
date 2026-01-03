from fastapi import HTTPException
from internal.repository import notice_repository_instance

class NoticeService:
    def __init__(self):
        self.notice_repository = notice_repository_instance

    def get_all_notices(self):
        try:
            notices = self.notice_repository.get_all_notices()
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception
        
        return notices
    
    def get_all_notices_by_month_and_year(self, year: int, month: int | None = None):
        try:
            notices = self.notice_repository.get_all_notices_by_month_and_year(year, month)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception
        
        return notices