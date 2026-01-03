from fastapi import HTTPException
from internal.repository import feedback_repository_instance

class FeedbackService:
    def __init__(self):
        self.feedback_repository = feedback_repository_instance

    async def get_all_feedbacks(self):
        try:
            feedbacks = await self.feedback_repository.get_all_feedbacks()
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception
        
        return feedbacks