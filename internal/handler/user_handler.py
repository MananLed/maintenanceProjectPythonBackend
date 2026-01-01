from fastapi import APIRouter, status
from internal.dto.user import (
    ChangePassword,
    UpdateProfile,
)
from internal.service import user_service_instance

user_router = APIRouter()


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


@user_router.get("/users")
def get_all_users():
    user_service_instance.get_all_users()
