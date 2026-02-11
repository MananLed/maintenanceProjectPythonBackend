from pydantic import Field, BaseModel
from enum import Enum
from uuid import uuid4


class UserRole(str, Enum):
    ROLEADMIN = "admin"
    ROLEOFFICER = "officer"
    ROLERESIDENT = "resident"

class User(BaseModel):
    first_name: str = Field(alias="first_name")
    middle_name: str = Field(alias="middle_name")
    last_name: str = Field(alias="last_name")
    mobile_number: str = Field(alias="mobile_number")
    email: str = Field(alias="email")
    flat: str = Field(alias="flat")
    password: str = Field(alias="password", exclude=True)
    role: UserRole = Field(alias="role", default=UserRole.ROLERESIDENT)
    id: str = Field(alias="id", default_factory = lambda: str(uuid4()))



