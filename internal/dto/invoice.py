from pydantic import BaseModel, Field


class InvoiceInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    amount: float = Field(gt=0, alias="amount")