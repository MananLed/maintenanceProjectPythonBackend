from fastapi import APIRouter
from internal.dto.notice import NoticeInput


notice_router = APIRouter()


@notice_router.post("/notices/issue")
def issue_notice(notice_input: NoticeInput):
    pass


@notice_router.get("/notices")
def get_all_notices():
    pass


@notice_router.get("/notices/month-year")
def get_notices_by_month_year():
    pass
