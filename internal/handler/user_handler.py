from fastapi import APIRouter
from models.user import LoginInput, SignUpInput, ChangePassword, UpdateProfile, OfficerDetails

user_router = APIRouter() 

@user_router.post("/login")
def login(login_input: LoginInput):
    pass

@user_router.post("/signup")
def signup(signup_input: SignUpInput):
    pass 

@user_router.get("/profile")
def profile():
    pass 

@user_router.patch("/profile/password")
def change_password(change_password_input: ChangePassword):
    pass 

@user_router.delete("/profile")
def delete_profile():
    pass 

@user_router.patch("/profile/update")
def update_profile(update_profile_input: UpdateProfile):
    pass
