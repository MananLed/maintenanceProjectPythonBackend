from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus
from internal.dto.feedback import FeedbackInput
from internal.response.response import Response
from internal.utils.jwt import verify_jwt
from internal.service import feedback_service_instance
from internal.constants.constants import SERVER_ERROR

feedback_router = APIRouter(dependencies=[Depends(verify_jwt)])


@feedback_router.post("/feedbacks/request")
def post_feedback(feedback_input: FeedbackInput):
    pass


@feedback_router.get("/feedbacks")
async def get_all_feedbacks():
    try:
        feedbacks = await feedback_service_instance.get_all_feedbacks()
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(feedbacks, "Feedbacks fetched successfully", HTTPStatus.OK)
