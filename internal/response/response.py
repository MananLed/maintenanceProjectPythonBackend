from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class Response:

    response_code_mapping = {401: 1001, 500: 1010}

    @classmethod
    def success_response(cls, data, message, status_code):

        return JSONResponse(
            status_code=status_code,
            content={"Status": "Success", "Message": message, "Data": jsonable_encoder(data)},
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
