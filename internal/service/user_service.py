from internal.repository import user_repository_instance
from internal.dto.user import LoginInput, SignInInput, ChangePassword
from internal.models.user import User, UserRole
from internal.utils.hash_and_check_password import compare_hash_and_password
from fastapi import HTTPException, status
from internal.utils.jwt import create_jwt_token
from internal.utils.hash_and_check_password import generate_hash_from_password
from uuid import UUID


class UserService:
    def __init__(self):
        self.user_repository = user_repository_instance

    async def change_password(self, change_password_input: ChangePassword, current_password: str, role: str, email: str, user_id: str):
        if not compare_hash_and_password(change_password_input.old_password, current_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Old password does'nt match")
        
        if compare_hash_and_password(change_password_input.new_password, current_password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No change in the password")
        
        try:
            new_hashed_password = generate_hash_from_password(change_password_input.new_password)
            await self.user_repository.change_password(new_hashed_password, role, email, user_id)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception  

    async def get_user_by_email_and_password(self, login_request: LoginInput):

        try:
            user: User = await self.user_repository.get_user_by_email(
                login_request.email
            )
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception

        if not compare_hash_and_password(login_request.password, user.password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        access_token = create_jwt_token(user.id, user.role, user.email, user.flat)

        return {"token": access_token, "email": user.email, "role": user.role}

    async def get_user_by_email(self, email):
        try:
            user: User = await self.user_repository.get_user_by_email(email)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception

        return user
    
    async def get_user_by_id_and_role(self, role: UserRole, id: UUID):
        try:
            user: User = await self.user_repository.get_user_by_id_and_role(role, id)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception

        return user
    
    async def add_user(self, sign_in_input: SignInInput, is_officer: bool | None = None):
        
        try:
            user: User = await self.get_user_by_email(sign_in_input.email)
        except HTTPException as exception:
            if exception.status_code == status.HTTP_401_UNAUTHORIZED:
                user = None
            else:
                raise exception

        if user is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "User with given email already exists")


        user: User = User.model_construct(**sign_in_input.model_dump())
        user.id = str(user.id)


        if is_officer == True:
            user.flat = "xxx"
            user.mobile_number = "xxxxxxxxxx"
            user.role = UserRole.ROLEOFFICER

        try:
            user.password = generate_hash_from_password(user.password)
        except:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error")

        try:
            await self.user_repository.add_user(user)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception
        
    async def update_profile(self, user: User, old_email: str | None = None):
        try:
            await self.user_repository.update_profile(user, old_email)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception    
