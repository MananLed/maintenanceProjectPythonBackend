from fastapi import APIRouter, HTTPException, Depends, Request, status
from http import HTTPStatus
from internal.dto.feedback import FeedbackInput
from internal.models.service_request import ServiceRequest, Status
from internal.models.user import User, UserRole
from internal.response.response import Response
from internal.utils.jwt import verify_jwt
from internal.service import feedback_service_instance, user_service_instance, request_service_instance
from internal.constants.constants import SERVER_ERROR
import uuid

feedback_router = APIRouter(dependencies=[Depends(verify_jwt)])


@feedback_router.post("/feedbacks/request")
async def post_feedback(feedback_input: FeedbackInput, request: Request):
    claims = request.state.user 

    try:
        user: User = await user_service_instance.get_user_by_id_and_role(UserRole(claims.get("role")), uuid.UUID(claims.get("user_id")))

        service_request: ServiceRequest = await request_service_instance.get_request_by_id(uuid.UUID(feedback_input.request_id))

        if user.id != service_request.resident_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized to perform the action")

        if service_request.status != Status.STATUSCOMPLETED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Feedback can only be given on completed request")

        await feedback_service_instance.post_feedback(user, service_request, feedback_input.rating, feedback_input.content)
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(None, "Feedback posted successfully", HTTPStatus.CREATED)



@feedback_router.get("/feedbacks")
async def get_all_feedbacks():
    try:
        feedbacks = await feedback_service_instance.get_all_feedbacks()
    except HTTPException as exception:
        return Response.error_response(exception.detail, exception.status_code)
    except Exception as exception:
        return Response.error_response(SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return Response.success_response(feedbacks, "Feedbacks fetched successfully", HTTPStatus.OK)
