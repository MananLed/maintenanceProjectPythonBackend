import pytest
from unittest.mock import MagicMock
import uuid
from internal.repository.request_repository import RequestRepository
from internal.models.service_request import ServiceRequest, ServiceType, Status
from internal.dto.service_request import RequestProviderInput
from internal.errors.base_exception import AppException
from internal.constants.constants import *

@pytest.fixture
def fake_deserializer():
    class FakeDeserializer:
        def deserialize(self, value):
            return list(value.values())[0]
    return FakeDeserializer

@pytest.fixture
def service_request_sample():
    return ServiceRequest.model_construct(
        request_id=uuid.uuid4(),
        resident_id="resident-123",
        flat="101",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        time_slot="09:00-09:45",
        date="2026-01-11",
        assigned_to="officer-1",
        feedback_given=False
    )

@pytest.mark.asyncio
async def test_book_request_success(fake_deserializer, service_request_sample):
    dynamodb = MagicMock()

    dynamodb.execute_statement.return_value = {"Items": []}

    dynamodb.execute_transaction.return_value = None

    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    result = await repo.book_request(service_request_sample)

    assert result is None
    assert dynamodb.execute_transaction.called

@pytest.mark.asyncio
async def test_book_request_conflict(fake_deserializer, service_request_sample):
    dynamodb = MagicMock()
 
    dynamodb.execute_statement.return_value = {"Items": [{"dummy": "data"}]}

    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.book_request(service_request_sample)

    assert exc.value.error_code == REQUEST_006


@pytest.mark.asyncio
async def test_book_request_dynamodb_exception(fake_deserializer, service_request_sample):
    dynamodb = MagicMock()

    dynamodb.execute_statement.return_value = {"Items": []}

    dynamodb.execute_transaction.side_effect = Exception("DB down")

    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.book_request(service_request_sample)

    assert exc.value.error_code == REQUEST_011

@pytest.mark.asyncio
async def test_update_request_status_with_assigned_to(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    request = ServiceRequest.model_construct(
        request_id=uuid.uuid4(),
        resident_id="resident-1",
        flat="101",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date="01-01-2026",
        time_slot="9:00-9:45",
        assigned_to="officer-1",
        feedback_given=False
    )

    assigned_to_input = RequestProviderInput.model_construct(assigned_to="officer-2")

    await repo.update_request_status(Status.STATUSAPPROVED, request, assigned_to_input)

    assert dynamodb.execute_transaction.called
    transact_calls = dynamodb.execute_transaction.call_args[1]["TransactStatements"]
    statements = [t["Statement"] for t in transact_calls]
    assert any("DELETE" in s for s in statements)
    assert any("INSERT" in s for s in statements)
    assert any("UPDATE" in s for s in statements)

@pytest.mark.asyncio
async def test_update_request_status_without_assigned_to(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    request = ServiceRequest.model_construct(
        request_id=uuid.uuid4(),
        resident_id="resident-1",
        flat="101",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date="01-01-2026",
        time_slot="9:00-9:45",
        assigned_to="officer-1",
        feedback_given=False
    )

    await repo.update_request_status(Status.STATUSAPPROVED, request)

    assert dynamodb.execute_transaction.called
    transact_calls = dynamodb.execute_transaction.call_args[1]["TransactStatements"]
    statements = [t["Statement"] for t in transact_calls]
    assert any("DELETE" in s for s in statements)
    assert any("INSERT" in s for s in statements)
    assert any("UPDATE" in s for s in statements)

@pytest.mark.asyncio
async def test_update_request_status_raises_app_exception(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_transaction.side_effect = Exception("DB failure")
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    request = ServiceRequest.model_construct(
        request_id=uuid.uuid4(),
        resident_id="resident-1",
        flat="101",
        service_type=ServiceType.PLUMBER,
        status=Status.STATUSPENDING,
        date="01-01-2026",
        time_slot="9:00-9:45",
        assigned_to="officer-1",
        feedback_given=False
    )

    with pytest.raises(AppException) as exc:
        await repo.update_request_status(Status.STATUSAPPROVED, request)

    assert exc.value.error_code == REQUEST_012
    

@pytest.mark.asyncio
async def test_get_requests_all_users(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request_id = str(uuid.uuid4())
    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "resident_id": {"S": "resident-1"},
                "flat_no": {"S": "101"},
                "time_slot": {"S": "9:00-9:45"},
                "service_type": {"S": f"{ServiceType.PLUMBER.value}"},
                "date": {"S": "01-01-2026"},
                "assigned_to": {"S": "officer-1"},
                "feedback_given": {"BOOL": False},
                "status": {"S": f"{Status.STATUSPENDING.value}"},
                "id": {"S": fake_request_id}
            }
        ]
    }

    requests = await repo.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSPENDING)

    assert len(requests) == 1
    assert isinstance(requests[0], ServiceRequest)
    assert requests[0].resident_id == "resident-1"
    assert requests[0].request_id == uuid.UUID(fake_request_id)
    dynamodb.execute_statement.assert_called_once()


@pytest.mark.asyncio
async def test_get_requests_for_resident(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request_id = str(uuid.uuid4())
    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "resident_id": {"S": "resident-2"},
                "flat_no": {"S": "102"},
                "time_slot": {"S": "10:00-10:45"},
                "service_type": {"S": f"{ServiceType.ELECTRICIAN.value}"},
                "date": {"S": "02-01-2026"},
                "assigned_to": {"S": "officer-2"},
                "feedback_given": {"BOOL": True},
                "status": {"S": f"{Status.STATUSAPPROVED.value}"},
                "id": {"S": fake_request_id}
            }
        ]
    }

    requests = await repo.get_requests_by_type_and_status(
        ServiceType.ELECTRICIAN, Status.STATUSAPPROVED, resident_id="resident-2"
    )

    assert len(requests) == 1
    assert requests[0].resident_id == "resident-2"
    assert requests[0].status == Status.STATUSAPPROVED
    dynamodb.execute_statement.assert_called_once()


@pytest.mark.asyncio
async def test_get_requests_raises_app_exception(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DB error")
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.get_requests_by_type_and_status(ServiceType.PLUMBER, Status.STATUSPENDING)

    assert exc.value.error_code == REQUEST_013


@pytest.mark.asyncio
async def test_get_request_by_id_success(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request_id = uuid.uuid4()
    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "resident_id": {"S": "resident-1"},
                "flat_no": {"S": "101"},
                "time_slot": {"S": "9:00-9:45"},
                "service_type": {"S": f"{ServiceType.PLUMBER.value}"},
                "date": {"S": "01-01-2026"},
                "assigned_to": {"S": "officer-1"},
                "feedback_given": {"BOOL": False},
                "status": {"S": f"{Status.STATUSPENDING.value}"},
                "id": {"S": str(fake_request_id)}
            }
        ]
    }

    request = await repo.get_request_by_id(fake_request_id)

    assert isinstance(request, ServiceRequest)
    assert request.request_id == fake_request_id
    assert request.resident_id == "resident-1"
    dynamodb.execute_statement.assert_called_once()


@pytest.mark.asyncio
async def test_get_request_by_id_not_found(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {"Items": []}
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request_id = uuid.uuid4()

    with pytest.raises(AppException) as exc:
        await repo.get_request_by_id(fake_request_id)

    assert exc.value.error_code == REQUEST_007


@pytest.mark.asyncio
async def test_get_request_by_id_db_error(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DB Error")
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request_id = uuid.uuid4()

    with pytest.raises(AppException) as exc:
        await repo.get_request_by_id(fake_request_id)

    assert exc.value.error_code == REQUEST_014


@pytest.mark.asyncio
async def test_reschedule_request_success(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request = ServiceRequest.model_construct(
        resident_id="resident-1",
        flat="101",
        time_slot="09:00-09:45",
        service_type=ServiceType.PLUMBER,
        date="01-01-2026",
        assigned_to="officer-1",
        feedback_given=False,
        status=Status.STATUSPENDING,
        request_id=uuid.uuid4()
    )

    await repo.reschedule_request("10:00-10:45", fake_request)

    assert dynamodb.execute_transaction.called
    calls = dynamodb.execute_transaction.call_args[1]["TransactStatements"]
    assert calls[0]["Parameters"][0]["S"] == "10:00-10:45"
    assert calls[1]["Parameters"][0]["S"] == "10:00-10:45"


@pytest.mark.asyncio
async def test_reschedule_request_db_error(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_transaction.side_effect = Exception("DB Error")
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request = ServiceRequest.model_construct(
        resident_id="resident-1",
        flat="101",
        time_slot="09:00-09:45",
        service_type=ServiceType.PLUMBER,
        date="01-01-2026",
        assigned_to="officer-1",
        feedback_given=False,
        status=Status.STATUSPENDING,
        request_id=uuid.uuid4()
    )

    with pytest.raises(AppException) as exc:
        await repo.reschedule_request("10:00-10:45", fake_request)

    assert exc.value.error_code == REQUEST_015


@pytest.mark.asyncio
async def test_delete_request_success(fake_deserializer):
    dynamodb = MagicMock()
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request = ServiceRequest.model_construct(
        resident_id="resident-1",
        flat="101",
        time_slot="09:00-09:45",
        service_type=ServiceType.PLUMBER,
        date="01-01-2026",
        assigned_to="officer-1",
        feedback_given=False,
        status=Status.STATUSPENDING,
        request_id=uuid.uuid4()
    )

    await repo.delete_request(fake_request)

    assert dynamodb.execute_transaction.called
    calls = dynamodb.execute_transaction.call_args[1]["TransactStatements"]
    assert calls[0]["Parameters"][0]["S"] == str(fake_request.request_id)
    assert calls[1]["Parameters"][1]["S"].startswith(fake_request.status.value)


@pytest.mark.asyncio
async def test_delete_request_db_error(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_transaction.side_effect = Exception("DB Error")
    repo = RequestRepository(dynamodb, "RequestTable", fake_deserializer)

    fake_request = ServiceRequest.model_construct(
        resident_id="resident-1",
        flat="101",
        time_slot="09:00-09:45",
        service_type=ServiceType.PLUMBER,
        date="01-01-2026",
        assigned_to="officer-1",
        feedback_given=False,
        status=Status.STATUSPENDING,
        request_id=uuid.uuid4()
    )

    with pytest.raises(AppException) as exc:
        await repo.delete_request(fake_request)

    assert exc.value.error_code == REQUEST_016
