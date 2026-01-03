from internal.models.service_request import ServiceType, Status, ServiceRequest
from fastapi import HTTPException
from typing import List
import asyncio
import uuid

class RequestRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

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
            
            request: ServiceRequest = ServiceRequest(request_details.get("resident_id"), request_details.get("flat_no"), request_details.get("time_slot"), 
                                                     ServiceType(request_details.get("service_type")), request_details.get("date"), request_details.get("assigned_to"), 
                                                     request_details.get("feedback_given"), Status(request_details.get("status")), uuid.UUID(request_details.get("id")))

            requests.append(request) 

        return requests