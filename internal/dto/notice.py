from pydantic import BaseModel, Field

class NoticeInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    content: str = Field(min_length=1, max_length=500, alias="content")