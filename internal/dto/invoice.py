from pydantic import BaseModel, Field, ConfigDict


class InvoiceInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    amount: float = Field(gt=0, alias="amount")