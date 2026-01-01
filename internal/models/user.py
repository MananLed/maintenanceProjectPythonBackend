from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class UserRole(str, Enum):
    ROLEADMIN = "admin"
    ROLEOFFICER = "officer"
    ROLERESIDENT = "resident"


@dataclass
class User:
    first_name: str = field(metadata={"json": "first_name"})
    middle_name: str = field(metadata={"json": "middle_name"})
    last_name: str = field(metadata={"json": "last_name"})
    mobile_number: str = field(metadata={"json": "mobile_number"})
    email: str = field(metadata={"json": "email"})
    flat: str = field(metadata={"json": "flat"})
    password: str = field(metadata={"json": "password"})
    role: UserRole = field(metadata={"json": "role"}, default=UserRole.ROLERESIDENT)
    id: str = field(metadata={"json": "id"}, default_factory=uuid4)



