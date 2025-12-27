from fastapi import APIRouter
from models.feedback import FeedbackInput

feedback_router = APIRouter()

@feedback_router.post("/feedbacks/request")
def post_feedback(feedback_input: FeedbackInput):
    pass


@feedback_router.get("/feedbacks")
def get_all_feedbacks():
    pass 

