from internal.models.service_request import ServiceType, Status, ServiceRequest
from internal.dto.service_request import RequestProviderInput
from fastapi import HTTPException, status
from typing import List
import asyncio
import uuid

class RequestRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    async def book_request(self, new_request: ServiceRequest):
        try:
            statuses_to_check = [Status.STATUSPENDING.value, Status.STATUSAPPROVED.value, Status.STATUSCOMPLETED.value]
            
            fetch_statement = f"SELECT * FROM \"{self.table_name}\" WHERE PK = ? AND begins_with(SK, ?)"
            
            for check_status in statuses_to_check:
                sk_prefix = f"{check_status}#{new_request.service_type.value}#{new_request.resident_id}#{new_request.date}#"
                
                response = await asyncio.to_thread( 
                    self.dynamodb.execute_statement,
                    Statement=fetch_statement,
                    Parameters=[{'S': 'REQUESTS'}, {'S': sk_prefix}]
                )
                
                if response.get("Items"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User already has a {check_status} request for this date"
                    )

            insert_statement = (
                f"INSERT INTO \"{self.table_name}\" VALUE "
                "{'PK': ?, 'SK': ?, 'assigned_to': ?, 'date': ?, 'feedback_given': ?, "
                "'flat_no': ?, 'id': ?, 'resident_id': ?, 'service_type': ?, 'status': ?, 'time_slot': ?}"
            )

            sk_status = f"{new_request.status.value}#{new_request.service_type.value}#{new_request.resident_id}#{new_request.date}#{str(new_request.request_id)}"
            sk_id = str(new_request.request_id)

            common_params = [
                {'S': new_request.assigned_to},
                {'S': new_request.date},
                {'BOOL': new_request.feedback_given},
                {'S': new_request.flat},
                {'S': str(new_request.request_id)},
                {'S': new_request.resident_id},
                {'S': str(new_request.service_type.value)},
                {'S': str(new_request.status.value)},
                {'S': new_request.time_slot}
            ]

            await asyncio.to_thread( 
                self.dynamodb.execute_transaction,
                TransactStatements=[
                    {
                        "Statement": insert_statement,
                        "Parameters": [{'S': 'REQUESTS'}, {'S': sk_status}] + common_params
                    },
                    {
                        "Statement": insert_statement,
                        "Parameters": [{'S': sk_id}, {'S': sk_id}] + common_params
                    }
                ]
            )
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception

    async def update_request_status(self, status_: Status, request: ServiceRequest, assigned_to: RequestProviderInput | None = None):
        update_statement = f"UPDATE {self.table_name} SET status = ?, assigned_to = ? WHERE PK = ? AND SK = ?"
        delete_statement = f"DELETE FROM {self.table_name} WHERE PK = ? AND SK = ?"
        insert_statement = (
                f"INSERT INTO \"{self.table_name}\" VALUE "
                "{'PK': ?, 'SK': ?, 'assigned_to': ?, 'date': ?, 'feedback_given': ?, "
                "'flat_no': ?, 'id': ?, 'resident_id': ?, 'service_type': ?, 'status': ?, 'time_slot': ?}"
            )
        
        common_params = [
                {'S': request.date},
                {'BOOL': request.feedback_given},
                {'S': request.flat},
                {'S': str(request.request_id)},
                {'S': request.resident_id},
                {'S': str(request.service_type.value)},
                {'S': str(status_.value)},
                {'S': request.time_slot}
            ]
        
        if assigned_to is not None:
            common_params = [{'S': assigned_to.assigned_to}] + common_params
            update_params = [
                            {"S": status_.value},
                            {"S": assigned_to.assigned_to},    
                            {"S": f"{request.request_id}"},       
                            {"S": f"{request.request_id}"},  
                        ]
        else:
            common_params = [{'S': request.assigned_to}] + common_params
            update_statement = f"UPDATE {self.table_name} SET status = ? WHERE PK = ? AND SK = ?"
            update_params = [
                            {"S": status_.value},    
                            {"S": f"{request.request_id}"},       
                            {"S": f"{request.request_id}"},  
                        ]
        
        sk_status = f"{status_.value}#{request.service_type.value}#{request.resident_id}#{request.date}#{str(request.request_id)}"
        
        try:
            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements=[
                    {
                        "Statement": delete_statement,
                        "Parameters": [  
                            {"S": "REQUESTS"},   
                            {"S": f"{request.status.value}#{request.service_type.value}#{request.resident_id}#{request.date}#{request.request_id}"}                 
                        ]
                    },
                    {
                        "Statement": insert_statement,
                        "Parameters": [{'S': 'REQUESTS'}, {'S': sk_status}] + common_params
                    },
                    {
                        "Statement": update_statement,
                        "Parameters": update_params
                    }
                ]
            )
        except Exception as exception:
            print(exception)
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Internal Server Error")


    async def get_requests_by_type_and_status(self, service_type: ServiceType, status: Status, resident_id: str | None = None):
        try:
            if resident_id is not None:
                sk_prefix = f"{status.value}#{service_type.value}#{resident_id}"
            else:
                sk_prefix = f"{status.value}#{service_type.value}"
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)",
                Parameters=[{"S": "REQUESTS"}, {"S": sk_prefix}]
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        items = response["Items"]

        requests: List[ServiceRequest] = []

        for item in items:
            request_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            
            request: ServiceRequest = ServiceRequest.model_construct(resident_id = request_details.get("resident_id"), flat =  request_details.get("flat_no"), time_slot = request_details.get("time_slot"), 
                                                     service_type = ServiceType(request_details.get("service_type")), date = request_details.get("date"), assigned_to = request_details.get("assigned_to"), 
                                                     feedback_given = bool(request_details.get("feedback_given")), status = Status(request_details.get("status")), request_id = uuid.UUID(request_details.get("id")))

            requests.append(request) 

        return requests
    
    async def get_request_by_id(self, id: uuid.UUID):
        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND SK = ?",
                Parameters=[{"S": str(id)}, {"S": str(id)}]
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        
        items = response["Items"]

        if len(items) == 0:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Request with given id not found.")
        
        for item in items:
            request_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

        request: ServiceRequest = ServiceRequest.model_construct(resident_id = request_details.get("resident_id"), flat =  request_details.get("flat_no"), time_slot = request_details.get("time_slot"), 
                                                     service_type = ServiceType(request_details.get("service_type")), date = request_details.get("date"), assigned_to = request_details.get("assigned_to"), 
                                                     feedback_given = bool(request_details.get("feedback_given")), status = Status(request_details.get("status")), request_id = uuid.UUID(request_details.get("id")))
        
        return request
    
    async def reschedule_request(self, new_time_slot, request: ServiceRequest):
        update_statement = f"UPDATE {self.table_name} SET time_slot = ? WHERE PK = ? AND SK = ?"

        try:
            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements=[
                    {
                        "Statement": update_statement,
                        "Parameters": [
                            {"S": new_time_slot},    
                            {"S": "REQUESTS"},   
                            {"S": f"{request.status.value}#{request.service_type.value}#{request.resident_id}#{request.date}#{request.request_id}"}                 
                        ]
                    },
                    {
                        "Statement": update_statement,
                        "Parameters": [
                            {"S": new_time_slot},    
                            {"S": f"{request.request_id}"},       
                            {"S": f"{request.request_id}"}  
                        ]
                    }
                ]
            )
        except Exception:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Internal Server Error")