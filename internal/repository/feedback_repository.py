from fastapi import HTTPException, status 
from typing import List 
from internal.models.feedback import Feedback
import asyncio
import uuid

class FeedbackRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    async def get_all_feedbacks(self):
        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                Parameters=[{"S": "FEEDBACKS"}]
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        items = response["Items"]

        feedbacks: List[Feedback] = []

        for item in items:
            feedback_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            feedback: Feedback = Feedback.model_construct(resident_id = feedback_details.get("resident_id"), flat = feedback_details.get("flat_no"),rating = int(feedback_details.get("rating")), 
                                          content = feedback_details.get("content"), resident_name = feedback_details.get("username"), request_id = uuid.UUID(feedback_details.get("request_id")), 
                                          assigned_to = feedback_details.get("assigned_to"), service_type = feedback_details.get("service_type"), date = feedback_details.get("date"), 
                                          time_slot = feedback_details.get("time_slot"), id = uuid.UUID(feedback_details.get("id")))
            
            feedbacks.append(feedback)

        return feedbacks