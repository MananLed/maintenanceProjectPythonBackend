from pydantic import BaseModel, Field, field_validator, EmailStr
import re

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$")

class SignUpInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    first_name: str = Field(min_length=1, max_length=26, alias="firstname")
    middle_name: str = Field(max_length=26, default="", alias="middlename")
    last_name: str = Field(min_length=1, max_length=26, alias="lastname")
    mobile_number: str = Field(
        min_length=10, max_length=10, pattern=r"^[6-9][0-9]{9}$", alias="mobile"
    )
    email: EmailStr = Field(alias="email")
    flat: str = Field(pattern=r"^[0-8]0[1-4]$", alias="flat")
    password: str = Field(min_length=12, alias="password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain uppercase, lowercase, digit, and special character"
            )
        return v


class LoginInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    email: EmailStr = Field(alias="email")
    password: str = Field(alias="password")


class OfficerDetails(LoginInput):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain uppercase, lowercase, digit, and special character"
            )
        return v


class ChangePassword(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    old_password: str = Field(alias="oldPassword")
    new_password: str = Field(alias="newPassword")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain uppercase, lowercase, digit, and special character"
            )
        return v


class UpdateProfile(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    first_name: str = Field(min_length=1, max_length=26, default="", alias="firstname")
    middle_name: str = Field(max_length=26, default="", alias="middlename")
    last_name: str = Field(min_length=1, max_length=26, default="", alias="lastname")
    mobile_number: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^[6-9][0-9]{9}$",
        default="",
        alias="mobile",
    )
    email: EmailStr = Field(default="", alias="email")