from pydantic import BaseModel, Field

class FeedbackInput(BaseModel):

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    rating: int = Field(min=1, max=5, alias="rating")
    content: str = Field(default="", max_length=500, alias="content")
    request_id: str = Field(alias="requestid")