from fastapi import status, APIRouter
from internal.dto.user import (
    LoginInput,
    SignUpInput,
)
from internal.response.response import Response
from http import HTTPStatus
from fastapi import HTTPException
from internal.constants.constants import SERVER_ERROR
from internal.service import user_service_instance

auth_router = APIRouter()


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
def login(login_input: LoginInput):

    try:
        response = user_service_instance.get_user_by_email_and_password(login_input)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(response, "Login Successful", HTTPStatus.OK)


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(signup_input: SignUpInput):
    pass
