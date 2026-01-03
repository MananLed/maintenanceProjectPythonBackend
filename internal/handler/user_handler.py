from fastapi import APIRouter, Request, HTTPException, Depends
from http import HTTPStatus
from internal.dto.user import (
    ChangePassword,
    UpdateProfile,
)
from internal.models.user import User
from internal.response.response import Response
from internal.utils.jwt import verify_jwt
from internal.service import user_service_instance
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
def change_password(change_password_input: ChangePassword):
    pass


@user_router.delete("/profile")
def delete_profile():
    pass


@user_router.patch("/profile/update")
def update_profile(update_profile_input: UpdateProfile):
    pass


@user_router.get("/users")
def get_all_users():
    user_service_instance.get_all_users()
