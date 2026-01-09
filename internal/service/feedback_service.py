from fastapi import HTTPException, status
from internal.models.user import User
from internal.models.service_request import ServiceRequest
from internal.models.feedback import Feedback 
from internal.constants.constants import *
from internal.errors.base_exception import AppException
from internal.repository import feedback_repository_instance
from typing import List

class FeedbackService:
    def __init__(self):
        self.feedback_repository = feedback_repository_instance

    async def post_feedback(self, user: User, request: ServiceRequest, rating: int, content: str):

        is_feedback_present: bool = await self.feedback_repository.is_feedback_present(request.request_id)

        if is_feedback_present:
            raise AppException(FEEDBACK_003)
        
        name_parts: List[str] = [user.first_name, user.middle_name, user.last_name]
        full_display_name: str = " ".join(filter(None, name_parts))

        feedback: Feedback = Feedback.model_construct(resident_id=user.id, flat=request.flat, rating=rating, 
                                        content=content, name= full_display_name, 
                                        request_id=request.request_id, assignedto=request.assigned_to, servicetype=request.service_type.value, 
                                        date=request.date, timeslot=request.time_slot)
        
        await self.feedback_repository.post_feedback(feedback)


    async def get_all_feedbacks(self):

        feedbacks = await self.feedback_repository.get_all_feedbacks()
        
        return feedbacks