from fastapi import HTTPException, status 
from typing import List 
from internal.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    def get_all_feedbacks(self):
        try:
            response = self.dynamodb.execute_statement(
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                Parameters=[{"S": "FEEDBACKS"}],
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        items = response["Items"]

        feedbacks: List[Feedback] = []

        for item in items:
            feedback_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            feedback: Feedback = Feedback(feedback_details.get("resident_id"), feedback_details.get("flat_no"), feedback_details.get("rating"), 
                                          feedback_details.get("content"), feedback_details.get("username"), feedback_details.get("request_id"), 
                                          feedback_details.get("assigned_to"), feedback_details.get("service_type"), feedback_details.get("date"), 
                                          feedback_details.get("time_slot"), feedback_details.get("id"))
            
            feedbacks.append(feedback)

        return feedbacks