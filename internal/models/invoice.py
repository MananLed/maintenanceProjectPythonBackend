from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Invoice(BaseModel):
    amount: float = Field(alias="amount")
    month: int = Field(alias="month")
    year: int = Field(alias="year")
    id: UUID = Field(alias="id", default_factory=uuid4)

