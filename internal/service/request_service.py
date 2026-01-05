from fastapi import HTTPException, status
from datetime import datetime
from typing import List
from uuid import UUID
from internal.repository import request_repository_instance
from internal.models.service_request import ServiceType, Status, ServiceRequest
from internal.dto.service_request import RequestProviderInput, ServiceRequestInput
from internal.utils.generate_time_slots import generate_time_slots, is_slot_in_past

class RequestService:
    def __init__(self):
        self.request_repository = request_repository_instance

    async def book_service(self, service_request_input: ServiceRequestInput, claims):
        try:
            available_slots = await self.get_available_time_slots(service_request_input.service_type)

            if service_request_input.slot_id < 1 or service_request_input.slot_id > len(available_slots):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request: Slot ID out of range"
                )
            
            chosen_slot = available_slots[service_request_input.slot_id - 1]

            user = claims

            now = datetime.now()

            new_request = ServiceRequest(
                resident_id=user.get("user_id"), 
                flat=user.get("flat"),
                time_slot=f"{chosen_slot.Label}",
                service_type=service_request_input.service_type,
                date=now.strftime("%d-%m-%Y"), 
                assigned_to="",
                feedback_given=False
            )

            await self.request_repository.book_request(new_request)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception

    async def update_request_status(self, status: Status, request_id: UUID, assigned_to: RequestProviderInput | None = None):
        try:
            await self.request_repository.update_request_status(status, request_id, assigned_to)
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception 

    async def get_requests_by_type_and_status(self, service_type: ServiceType, status: Status, resident_id: str | None = None):
        try:
            requests: List[ServiceRequest] = await self.request_repository.get_requests_by_type_and_status(service_type, status, resident_id)
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception
        
        return requests
    
    async def get_available_time_slots(self, service_type: ServiceType):
        try:
            pending_request: List[ServiceRequest] = await self.get_requests_by_type_and_status(service_type, Status.STATUSPENDING)
            approved_request: List[ServiceRequest] = await self.get_requests_by_type_and_status(service_type, Status.STATUSAPPROVED)
            completed_request: List[ServiceRequest] = await self.get_requests_by_type_and_status(service_type, Status.STATUSCOMPLETED)
        except HTTPException as exception:
            raise exception
        except Exception as exception:
            raise exception
        
        active_requests = pending_request + approved_request + completed_request

        today_str = datetime.now().strftime("%d-%m-%Y")
        booked_labels = {req.time_slot for req in active_requests if req.date == today_str}

        all_time_slots = generate_time_slots()

        available_slots = []
        for slot in all_time_slots:
            if slot.Label in booked_labels:
                continue

            if is_slot_in_past(slot.Label, today_str):
                continue
                
            available_slots.append(slot)

        return available_slots