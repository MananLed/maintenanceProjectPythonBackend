from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict, model_validator, TypeAdapter
import re

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$")
MOBILE_REGEX = re.compile(r"^[6-9][0-9]{9}$")

class SignInInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    first_name: str = Field(min_length=1, max_length=26, alias="firstName")
    middle_name: str = Field(max_length=26, default="", alias="middleName")
    last_name: str = Field(min_length=1, max_length=26, alias="lastName")
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

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    email: EmailStr = Field(alias="email")
    password: str = Field(alias="password")


class OfficerDetails(LoginInput):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain uppercase, lowercase, digit, and special character"
            )
        return v


class ChangePassword(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

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

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    first_name: str = Field(default="", alias="firstname")
    middle_name: str = Field(default="", alias="middlename")
    last_name: str = Field(default="", alias="lastname")
    mobile_number: str = Field(default="", alias="mobile")
    email: str = Field(default="", alias="email")

    @model_validator(mode="after")
    def validate_fields(self):

        first_name = self.first_name
        last_name = self.last_name
        middle_name = self.middle_name
        mobile = self.mobile_number
        email = self.email

        if first_name != "":
            if len(first_name) < 1:
                raise ValueError("first_name must have at least 1 character")
            if len(first_name) > 26:
                raise ValueError("first_name must be at most 26 characters")

        if last_name != "":
            if len(last_name) < 1:
                raise ValueError("last_name must have at least 1 character")
            if len(last_name) > 26:
                raise ValueError("last_name must be at most 26 characters")

        if middle_name != "":
            if len(middle_name) > 26:
                raise ValueError("middle_name must be at most 26 characters")

        if mobile != "":
            if not MOBILE_REGEX.match(mobile):
                raise ValueError("mobile number must be 10 digits starting with 6-9")

        if email != "":
            try:
                TypeAdapter(EmailStr).validate_python(email)
            except Exception:
                raise ValueError("email must be a valid email address")

        return self