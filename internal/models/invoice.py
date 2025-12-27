from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


@dataclass
class Invoice:
    amount: float = field(metadata={"json": "amount"})
    month: int = field(metadata={"json": "month"})
    year: int = field(metadata={"json": "year"})
    id: UUID = field(metadata={"json": "id"}, default_factory=uuid4)


class InvoiceInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    amount: float = Field(gt=0, alias="amount")
