from fastapi import APIRouter, Depends, Query
from typing import Annotated
from http import HTTPStatus
from internal.dto.notice import NoticeInput
from internal.response.response import Response
from internal.models.user import UserRole
from internal.utils.jwt import verify_jwt
from internal.dependencies.authorization import require_roles
from internal.service import notice_service_instance

notice_router = APIRouter(dependencies=[Depends(verify_jwt)])


@notice_router.post("/notices/issue", dependencies=[Depends(require_roles(UserRole.ROLEADMIN, UserRole.ROLEOFFICER))])
async def issue_notice(notice_input: NoticeInput):
        
    await notice_service_instance.issue_notice(notice_input)
    
    return Response.success_response(None, "Notice issued successfully", HTTPStatus.CREATED)
    
    


@notice_router.get("/notices")
async def get_all_notices():

    notices = await notice_service_instance.get_all_notices()
    
    return Response.success_response(notices, "Notices fetched successfully", HTTPStatus.OK)


@notice_router.get("/notices/month-year")
async def get_notices_by_month_year(year: Annotated[int, Query(gt=0)], month: Annotated[int | None, Query(gt=0, lt=13)] = None):

    notices = await notice_service_instance.get_all_notices_by_month_and_year(year, month)
    
    return Response.success_response(notices, "Notices fetched successfully", HTTPStatus.OK)
