from fastapi import HTTPException
from typing import List
from internal.repository import request_repository_instance
from internal.models.service_request import ServiceType, Status, ServiceRequest

class RequestService:
    def __init__(self):
        self.request_repository = request_repository_instance

    async def get_requests_by_type_and_status(self, service_type: ServiceType, status: Status, resident_id: str | None = None):
        try:
            requests: List[ServiceRequest] = await self.request_repository.get_requests_by_type_and_status(service_type, status, resident_id)
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception
        
        return requests