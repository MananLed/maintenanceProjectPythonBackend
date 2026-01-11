from typing import List 
from internal.models.feedback import Feedback
from internal.models.service_request import Status
from internal.errors.base_exception import AppException
from internal.constants.constants import *
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
            raise AppException(FEEDBACK_004)

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
    
    async def is_feedback_present(self, request_id: uuid.UUID) -> bool:
        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                Parameters=[{"S": "FEEDBACKS"}, {"S": str(request_id)}]
            )
        except:
            raise AppException(FEEDBACK_005)

        items = response["Items"]

        if len(items) == 0:
            return False 
        else:
            return True
    
    async def post_feedback(self, feedback: Feedback):
        statement = (
            f"INSERT INTO \"{self.table_name}\" VALUE "
            "{'PK': ?, 'SK': ?, 'assigned_to': ?, 'content': ?, 'date': ?, "
            "'flat_no': ?, 'id': ?, 'rating': ?, 'request_id': ?, 'resident_id': ?, "
            "'service_type': ?, 'time_slot': ?, 'username': ?}"
        )

        update_statement = f'UPDATE "{self.table_name}" SET feedback_given = ? WHERE PK = ? AND SK = ?'

        parameters = [
            {"S": "FEEDBACKS"},                                  
            {"S": f"{str(feedback.request_id)}#{str(feedback.id)}"},         
            {"S": feedback.assigned_to},                          
            {"S": feedback.content},                              
            {"S": feedback.date},                                 
            {"S": feedback.flat},                                  
            {"S": str(feedback.id)},                                 
            {"N": str(feedback.rating)},                           
            {"S": str(feedback.request_id)},                        
            {"S": feedback.resident_id},                            
            {"S": feedback.service_type},                           
            {"S": feedback.time_slot},                              
            {"S": feedback.resident_name}                                     
        ]

        sk_requests = f"{Status.STATUSCOMPLETED.value}#{feedback.service_type}#{feedback.resident_id}#{feedback.date}#{feedback.request_id}"

        try:
            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements = [
                    {
                        "Statement":statement,
                        "Parameters":parameters
                    },
                    {
                        "Statement": update_statement,
                        "Parameters": [
                            {"BOOL": True},         
                            {"S": str(feedback.request_id)},
                            {"S": str(feedback.request_id)}  
                        ]
                    },
                    {
                        "Statement": update_statement,
                        "Parameters": [
                            {"BOOL": True},   
                            {"S": "REQUESTS"}, 
                            {"S": sk_requests} 
                        ]   
                    }
                ]
            )
        except:
            raise AppException(FEEDBACK_006)
        