from fastapi import status, APIRouter
from internal.dto.user import (
    LoginInput,
    SignInInput,
)
from internal.response.response import Response
from http import HTTPStatus
from fastapi import HTTPException
from internal.constants.constants import SERVER_ERROR
from internal.service import user_service_instance
import time

auth_router = APIRouter()


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(login_input: LoginInput):
    try:
        response = await user_service_instance.get_user_by_email_and_password(login_input)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(response, "Login Successful", HTTPStatus.CREATED)


@auth_router.post("/signin", status_code=status.HTTP_201_CREATED)
async def signup(sign_in_input: SignInInput):
    try:
        await user_service_instance.add_user(sign_in_input)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Sign in Successful", HTTPStatus.CREATED)
