from fastapi.responses import JSONResponse
from dataclasses import is_dataclass, asdict
from pydantic import BaseModel


class Response:

    response_code_mapping = {401: 1001, 500: 1010}

    @classmethod
    def success_response(cls, data, message, status_code):

        if is_dataclass(data):
            data = asdict(data)
        elif isinstance(data, BaseModel):
            data = data.model_dump()

        return JSONResponse(
            status_code=status_code,
            content={"Status": "Success", "Message": message, "Data": data},
        )

    @classmethod
    def error_response(cls, error_message, status_code):
        return JSONResponse(
            status_code=status_code,
            content={
                "Status": "fail",
                "Message": error_message,
                "ErrorCode": cls.response_code_mapping.get(status_code, 1011),
            },
        )
