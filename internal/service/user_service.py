from internal.repository import user_repository_instance
from internal.dto.user import LoginInput
from internal.models.user import User
from internal.utils.hash_and_check_password import compare_hash_and_password
from fastapi import HTTPException, status
from internal.utils.jwt import create_jwt_token

class UserService:
    def __init__(self):
        self.user_repository = user_repository_instance

    def get_all_users(self):
        self.user_repository.get_all_user_details()

    def get_user_by_email_and_password(self, login_request: LoginInput):
        
        user: User = self.user_repository.get_user_by_email(login_request.email)

        if not compare_hash_and_password(login_request.password, user.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        
        access_token = create_jwt_token(user.id, user.role, user.email, user.flat)

        return {"token": access_token, "email": user.email, "role": user.role}
