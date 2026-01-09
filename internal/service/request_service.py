from datetime import datetime
from typing import List
from uuid import UUID
from internal.repository import request_repository_instance
from internal.models.service_request import ServiceType, Status, ServiceRequest
from internal.errors.base_exception import AppException
from internal.constants.constants import *
from internal.dto.service_request import RequestProviderInput, ServiceRequestInput, RescheduleRequestInput
from internal.utils.generate_time_slots import generate_time_slots, is_slot_in_past

class RequestService:
    def __init__(self):
        self.request_repository = request_repository_instance

    async def book_service(self, service_request_input: ServiceRequestInput, claims):
            
        available_slots = await self.get_available_time_slots(service_request_input.service_type)

        if service_request_input.slot_id < 1 or service_request_input.slot_id > len(available_slots):
            raise AppException(REQUEST_002)
        
        chosen_slot = available_slots[service_request_input.slot_id - 1]

        user = claims

        now = datetime.now()
        

        new_request: ServiceRequest = ServiceRequest.model_construct(
            resident_id = user.get("user_id"), 
            flat = user.get("flat"),
            time_slot = f"{chosen_slot.Label}",
            service_type = service_request_input.service_type,
            date = now.strftime("%d-%m-%Y")
        )

        await self.request_repository.book_request(new_request)
        
    async def reschedule_request(self, id: UUID, reschedule_request_input: RescheduleRequestInput, claims):

        request: ServiceRequest = await self.request_repository.get_request_by_id(id)

        if claims.get("user_id") != str(request.resident_id):
            raise AppException(REQUEST_009)

        if request.status == Status.STATUSAPPROVED or request.status == Status.STATUSCOMPLETED:
            raise AppException(REQUEST_005)
        
        available_slots = await self.get_available_time_slots(request.service_type)

        if reschedule_request_input.slot_id < 1 or reschedule_request_input.slot_id > len(available_slots):
            raise AppException(REQUEST_010)
        
        chosen_slot = available_slots[reschedule_request_input.slot_id - 1]

        await self.request_repository.reschedule_request(str(chosen_slot.Label), request)

        
    async def get_request_by_id(self, request_id: UUID):

        request: ServiceRequest = await self.request_repository.get_request_by_id(request_id)
    
        return request
        

    async def update_request_status(self, status_: Status, request_id: UUID, assigned_to: RequestProviderInput | None = None):

        request: ServiceRequest = await self.request_repository.get_request_by_id(request_id)

        if status_ == Status.STATUSAPPROVED:
            if request.status != Status.STATUSPENDING:
                raise AppException(REQUEST_003)
        elif status_ == Status.STATUSCOMPLETED:
            if request.status != Status.STATUSAPPROVED:
                raise AppException(REQUEST_004)
        
        await self.request_repository.update_request_status(status_, request, assigned_to)

    async def get_requests_by_type_and_status(self, service_type: ServiceType, status: Status, resident_id: str | None = None):
        
        requests: List[ServiceRequest] = await self.request_repository.get_requests_by_type_and_status(service_type, status, resident_id)
        
        return requests
    
    async def get_available_time_slots(self, service_type: ServiceType):

        pending_request: List[ServiceRequest] = await self.get_requests_by_type_and_status(service_type, Status.STATUSPENDING)
        approved_request: List[ServiceRequest] = await self.get_requests_by_type_and_status(service_type, Status.STATUSAPPROVED)
        completed_request: List[ServiceRequest] = await self.get_requests_by_type_and_status(service_type, Status.STATUSCOMPLETED)

        
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
    
    async def delete_request(self, service_request: ServiceRequest):

        await self.request_repository.delete_request(service_request)
