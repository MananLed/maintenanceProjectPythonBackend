import pytest
from unittest.mock import AsyncMock
from internal.service.request_service import RequestService
from internal.dto.service_request import ServiceRequestInput, RescheduleRequestInput, RequestProviderInput
from internal.models.service_request import ServiceType, ServiceRequest, Status
from internal.errors.base_exception import AppException
from internal.constants.constants import *
from uuid import uuid4
from datetime import datetime

@pytest.mark.asyncio
async def test_book_service_success(mocker):
    service = RequestService()

    mock_slot = mocker.Mock()
    mock_slot.Label = "09:00 - 09:45"

    mocker.patch.object(
        service,
        "get_available_time_slots",
        AsyncMock(return_value=[mock_slot])
    )

    mock_book_request = AsyncMock()
    mocker.patch.object(
        service.request_repository,
        "book_request",
        mock_book_request
    )

    service_request_input = ServiceRequestInput(
        service_type=ServiceType.PLUMBER,
        slot_id=1
    )

    claims = {
        "user_id": "resident-123",
        "flat": "A-101"
    }

    await service.book_service(service_request_input, claims)

    mock_book_request.assert_called_once()

    saved_request = mock_book_request.call_args[0][0]

    assert saved_request.resident_id == "resident-123"
    assert saved_request.flat == "A-101"
    assert saved_request.time_slot == "09:00 - 09:45"
    assert saved_request.service_type == ServiceType.PLUMBER


@pytest.mark.asyncio
async def test_book_service_invalid_slot_id(mocker):
    service = RequestService()

    mock_slot = mocker.Mock()
    mock_slot.Label = "09:00 - 09:45"

    mocker.patch.object(
        service,
        "get_available_time_slots",
        AsyncMock(return_value=[mock_slot])
    )

    service_request_input = ServiceRequestInput(
        servicetype=ServiceType.ELECTRICIAN,
        slotid=2  
    )

    claims = {
        "user_id": "resident-123",
        "flat": "A-101"
    }

    with pytest.raises(AppException) as exc:
        await service.book_service(service_request_input, claims)

    assert exc.value.error_code == "REQUEST_002"


@pytest.mark.asyncio
async def test_reschedule_request_success(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    mock_slot = mocker.Mock()
    mock_slot.Label = "10:30 - 11:15"

    mocker.patch.object(
        service,
        "get_available_time_slots",
        AsyncMock(return_value=[mock_slot])
    )

    mock_reschedule = AsyncMock()
    mocker.patch.object(
        service.request_repository,
        "reschedule_request",
        mock_reschedule
    )

    reschedule_input = RescheduleRequestInput(slot_id=1)

    claims = {
        "user_id": "user-123"
    }

    await service.reschedule_request(request_id, reschedule_input, claims)

    mock_reschedule.assert_called_once_with(
        "10:30 - 11:15",
        request
    )

@pytest.mark.asyncio
async def test_reschedule_request_user_not_owner(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.ELECTRICIAN,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    reschedule_input = RescheduleRequestInput(slot_id=1)

    claims = {
        "user_id": "user-999"
    }

    with pytest.raises(AppException) as exc:
        await service.reschedule_request(request_id, reschedule_input, claims)

    assert exc.value.error_code == REQUEST_009

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [Status.STATUSAPPROVED, Status.STATUSCOMPLETED]
)
async def test_reschedule_request_invalid_status(mocker, status):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=status
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    reschedule_input = RescheduleRequestInput(slot_id=1)

    claims = {
        "user_id": "user-123"
    }

    with pytest.raises(AppException) as exc:
        await service.reschedule_request(request_id, reschedule_input, claims)

    assert exc.value.error_code == REQUEST_005

@pytest.mark.asyncio
async def test_reschedule_request_slot_id_less_than_one(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    reschedule_input = RescheduleRequestInput(slot_id=0)

    claims = {
        "user_id": "user-123"
    }

    with pytest.raises(AppException) as exc:
        await service.reschedule_request(request_id, reschedule_input, claims)

    assert exc.value.error_code == REQUEST_010


@pytest.mark.asyncio
async def test_reschedule_request_slot_id_less_than_one(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    reschedule_input = RescheduleRequestInput(slot_id=0)

    claims = {
        "user_id": "user-123"
    }

    with pytest.raises(AppException) as exc:
        await service.reschedule_request(request_id, reschedule_input, claims)

    assert exc.value.error_code == REQUEST_010


@pytest.mark.asyncio
async def test_reschedule_request_slot_id_out_of_range(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.ELECTRICIAN,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    mock_slot = mocker.Mock()
    mock_slot.Label = "09:00 - 09:45"

    mocker.patch.object(
        service,
        "get_available_time_slots",
        AsyncMock(return_value=[mock_slot])
    )

    reschedule_input = RescheduleRequestInput(slot_id=2)

    claims = {
        "user_id": "user-123"
    }

    with pytest.raises(AppException) as exc:
        await service.reschedule_request(request_id, reschedule_input, claims)

    assert exc.value.error_code == REQUEST_010


@pytest.mark.asyncio
async def test_reschedule_request_no_available_slots(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    mocker.patch.object(
        service,
        "get_available_time_slots",
        AsyncMock(return_value=[])
    )

    reschedule_input = RescheduleRequestInput(slot_id=1)

    claims = {
        "user_id": "user-123"
    }

    with pytest.raises(AppException) as exc:
        await service.reschedule_request(request_id, reschedule_input, claims)

    assert exc.value.error_code == REQUEST_010


@pytest.mark.asyncio
async def test_get_request_by_id_success(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING
    )

    mock_get_request = AsyncMock(return_value=request)

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        mock_get_request
    )

    result = await service.get_request_by_id(request_id)

    assert result == request
    mock_get_request.assert_called_once_with(request_id)


@pytest.mark.asyncio
async def test_update_request_status_approve_success(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    mock_update = AsyncMock()
    mocker.patch.object(
        service.request_repository,
        "update_request_status",
        mock_update
    )

    provider = RequestProviderInput.model_construct(
        assignedto="df"
    )

    await service.update_request_status(
        Status.STATUSAPPROVED,
        request_id,
        provider
    )

    mock_update.assert_called_once_with(
        Status.STATUSAPPROVED,
        request,
        provider
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_status",
    [
        Status.STATUSAPPROVED,
        Status.STATUSCOMPLETED
    ]
)
async def test_update_request_status_approve_invalid_state(mocker, current_status):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.ELECTRICIAN,
        status=current_status
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    with pytest.raises(AppException) as exc:
        await service.update_request_status(
            Status.STATUSAPPROVED,
            request_id
        )

    assert exc.value.error_code == REQUEST_003


@pytest.mark.asyncio
async def test_update_request_status_complete_success(mocker):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSAPPROVED
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    mock_update = AsyncMock()
    mocker.patch.object(
        service.request_repository,
        "update_request_status",
        mock_update
    )

    await service.update_request_status(
        Status.STATUSCOMPLETED,
        request_id
    )

    mock_update.assert_called_once_with(
        Status.STATUSCOMPLETED,
        request,
        None
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_status",
    [
        Status.STATUSPENDING,
        Status.STATUSCOMPLETED
    ]
)
async def test_update_request_status_complete_invalid_state(mocker, current_status):
    service = RequestService()
    request_id = uuid4()

    request = ServiceRequest.model_construct(
        resident_id="user-123",
        service_type=ServiceType.PLUMBER,
        status=current_status
    )

    mocker.patch.object(
        service.request_repository,
        "get_request_by_id",
        AsyncMock(return_value=request)
    )

    with pytest.raises(AppException) as exc:
        await service.update_request_status(
            Status.STATUSCOMPLETED,
            request_id
        )

    assert exc.value.error_code == REQUEST_004

FIXED_DATE = datetime(2026, 1, 11)
FIXED_DATE_STR = "11-01-2026"


@pytest.mark.asyncio
async def test_get_requests_by_type_and_status_filters_today(mocker):
    service = RequestService()

    request_today_1 = ServiceRequest.model_construct(
        resident_id="user-1",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date=FIXED_DATE_STR
    )

    request_today_2 = ServiceRequest.model_construct(
        resident_id="user-2",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date=FIXED_DATE_STR
    )

    request_old = ServiceRequest.model_construct(
        resident_id="user-3",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date="10-01-2026"
    )

    mocker.patch.object(
        service.request_repository,
        "get_requests_by_type_and_status",
        AsyncMock(return_value=[request_today_1, request_today_2, request_old])
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_requests_by_type_and_status(
        ServiceType.PLUMBER,
        Status.STATUSPENDING
    )

    assert result == [request_today_1, request_today_2]

@pytest.mark.asyncio
async def test_get_requests_by_type_and_status_with_resident_id(mocker):
    service = RequestService()
    resident_id = "user-123"

    request_today = ServiceRequest.model_construct(
        resident_id=resident_id,
        service_type=ServiceType.ELECTRICIAN,
        status=Status.STATUSAPPROVED,
        date=FIXED_DATE_STR
    )

    mock_repo = AsyncMock(return_value=[request_today])

    mocker.patch.object(
        service.request_repository,
        "get_requests_by_type_and_status",
        mock_repo
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_requests_by_type_and_status(
        ServiceType.ELECTRICIAN,
        Status.STATUSAPPROVED,
        resident_id
    )

    assert result == [request_today]
    mock_repo.assert_called_once_with(
        ServiceType.ELECTRICIAN,
        Status.STATUSAPPROVED,
        resident_id
    )


@pytest.mark.asyncio
async def test_get_requests_by_type_and_status_no_today_requests(mocker):
    service = RequestService()

    old_request = ServiceRequest.model_construct(
        resident_id="user-1",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date="09-01-2026"
    )

    mocker.patch.object(
        service.request_repository,
        "get_requests_by_type_and_status",
        AsyncMock(return_value=[old_request])
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_requests_by_type_and_status(
        ServiceType.PLUMBER,
        Status.STATUSPENDING
    )

    assert result == []

@pytest.mark.asyncio
async def test_get_requests_by_type_and_status_empty_repo_result(mocker):
    service = RequestService()

    mocker.patch.object(
        service.request_repository,
        "get_requests_by_type_and_status",
        AsyncMock(return_value=[])
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_requests_by_type_and_status(
        ServiceType.PLUMBER,
        Status.STATUSPENDING
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_available_time_slots_filters_booked_and_past(mocker):
    service = RequestService()

    booked_request = ServiceRequest.model_construct(
        resident_id="user-1",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        time_slot="09:00 - 09:45",
        date=FIXED_DATE_STR
    )

    mocker.patch.object(
        service,
        "get_requests_by_type_and_status",
        AsyncMock(side_effect=[
            [booked_request], 
            [],    
            []                
        ])
    )

    slot_booked = mocker.Mock()
    slot_booked.Label = "09:00 - 09:45"

    slot_past = mocker.Mock()
    slot_past.Label = "08:00 - 08:45"

    slot_available = mocker.Mock()
    slot_available.Label = "10:00 - 10:45"

    mocker.patch(
        "internal.service.request_service.generate_time_slots",
        return_value=[slot_booked, slot_past, slot_available]
    )

    mocker.patch(
        "internal.service.request_service.is_slot_in_past",
        side_effect=lambda label, _: label == "08:00 - 08:45"
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_available_time_slots(ServiceType.PLUMBER)

    assert result == [slot_available]


@pytest.mark.asyncio
async def test_get_available_time_slots_no_active_requests(mocker):
    service = RequestService()

    mocker.patch.object(
        service,
        "get_requests_by_type_and_status",
        AsyncMock(return_value=[])
    )

    slot1 = mocker.Mock()
    slot1.Label = "10:00 - 10:45"

    slot2 = mocker.Mock()
    slot2.Label = "11:00 - 11:45"

    mocker.patch(
        "internal.service.request_service.generate_time_slots",
        return_value=[slot1, slot2]
    )

    mocker.patch(
        "internal.service.request_service.is_slot_in_past",
        return_value=False
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_available_time_slots(ServiceType.ELECTRICIAN)

    assert result == [slot1, slot2]

@pytest.mark.asyncio
async def test_get_available_time_slots_all_slots_booked(mocker):
    service = RequestService()

    booked_request = ServiceRequest.model_construct(
        resident_id="user-1",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSAPPROVED,
        time_slot="10:00 - 10:45",
        date=FIXED_DATE_STR
    )

    mocker.patch.object(
        service,
        "get_requests_by_type_and_status",
        AsyncMock(side_effect=[
            [],
            [booked_request],
            []
        ])
    )

    slot = mocker.Mock()
    slot.Label = "10:00 - 10:45"

    mocker.patch(
        "internal.service.request_service.generate_time_slots",
        return_value=[slot]
    )

    mocker.patch(
        "internal.service.request_service.is_slot_in_past",
        return_value=False
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_available_time_slots(ServiceType.PLUMBER)

    assert result == []


@pytest.mark.asyncio
async def test_get_available_time_slots_all_slots_in_past(mocker):
    service = RequestService()

    mocker.patch.object(
        service,
        "get_requests_by_type_and_status",
        AsyncMock(return_value=[])
    )

    slot = mocker.Mock()
    slot.Label = "08:00 - 08:45"

    mocker.patch(
        "internal.service.request_service.generate_time_slots",
        return_value=[slot]
    )

    mocker.patch(
        "internal.service.request_service.is_slot_in_past",
        return_value=True
    )

    mock_datetime = mocker.patch(
        "internal.service.request_service.datetime"
    )
    mock_datetime.now.return_value = FIXED_DATE
    mock_datetime.now.strftime = datetime.strftime

    result = await service.get_available_time_slots(ServiceType.PLUMBER)

    assert result == []
