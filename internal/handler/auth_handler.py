from fastapi import status, APIRouter
from internal.dto.user import (
    LoginInput,
    SignUpInput,
)
from internal.service import user_service_instance

auth_router = APIRouter()

@auth_router.post("/login", status_code = status.HTTP_201_CREATED)
def login(login_input: LoginInput):
    
    return user_service_instance.get_user_by_email_and_password(login_input)

    



@auth_router.post("/signup", status_code = status.HTTP_201_CREATED)
def signup(signup_input: SignUpInput):
    pass
