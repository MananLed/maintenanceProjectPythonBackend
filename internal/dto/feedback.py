from pydantic import BaseModel, Field, ConfigDict

class FeedbackInput(BaseModel):

    model_config = ConfigDict(populate_by_name=True, extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    rating: int = Field(ge=1, le=5, alias="rating")
    content: str = Field(default="", max_length=500, alias="content")
    request_id: str = Field(alias="requestid", max_length=1000)