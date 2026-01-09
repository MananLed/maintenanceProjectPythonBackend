from fastapi import status, APIRouter
from internal.dto.user import (
    LoginInput,
    SignInInput,
)
from internal.response.response import Response
from http import HTTPStatus
from internal.dependencies.dependencies import sns_client
from internal.constants.constants import INVOICE_EMAIL_TOPIC_ARN
from internal.service import user_service_instance

auth_router = APIRouter()


@auth_router.post("/login")
async def login(login_input: LoginInput):
    
    response = await user_service_instance.get_user_by_email_and_password(login_input)
    
    return Response.success_response(response, "Login Successful", HTTPStatus.CREATED)


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(sign_in_input: SignInInput):

    await user_service_instance.add_user(sign_in_input)
    sns_client.subscribe(
        TopicArn= INVOICE_EMAIL_TOPIC_ARN,
        Protocol="email",
        Endpoint= str(sign_in_input.email)
    )
    
    return Response.success_response(None, "Sign in Successful", HTTPStatus.CREATED)
