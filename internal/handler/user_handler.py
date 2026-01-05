from fastapi import APIRouter, Request, HTTPException, Depends
from http import HTTPStatus
from internal.dto.user import (
    ChangePassword,
    UpdateProfile,
)
from internal.models.user import User
from internal.response.response import Response
from internal.models.user import UserRole
import uuid
from internal.utils.jwt import verify_jwt
from internal.service import user_service_instance, society_service_instance
from internal.constants.constants import SERVER_ERROR


user_router = APIRouter(dependencies=[Depends(verify_jwt)])


@user_router.get("/profile")
async def get_profile(request: Request):

    claims = request.state.user

    try:
        user: User = await user_service_instance.get_user_by_email(claims.get("email"))
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(user, "Profile fetched successfully", HTTPStatus.OK)


@user_router.patch("/profile/password")
async def change_password(change_password_input: ChangePassword, request: Request):
    try:
        claims = request.state.user
        user: User = await user_service_instance.get_user_by_email(claims.get("email"))
        await user_service_instance.change_password(change_password_input, user.password, user.role, user.email, user.id)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Password changed successfully", HTTPStatus.OK)


@user_router.delete("/profile")
async def delete_profile(request: Request):
    claims = request.state.user 

    try:
        await society_service_instance.delete_user(uuid.UUID(claims.get("user_id")), UserRole(claims.get("role")))
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Profile deleted successfully", HTTPStatus.OK)

@user_router.patch("/profile/update")
def update_profile(update_profile_input: UpdateProfile):
    pass
