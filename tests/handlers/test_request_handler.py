from internal.models.user import UserRole
from internal.models.service_request import ServiceType, Status, ServiceRequest
from http import HTTPStatus
from fastapi import HTTPException
from uuid import uuid4


def test_book_service_success(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.book_service",
        return_value=None,
    )

    response = client.post(
        "/service",
        json={
            "slotid": 3,
            "servicetype": ServiceType.PLUMBER,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Service request booked successfully"
    assert body["data"] is None


def test_book_service_unauthorized(client, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    response = client.post(
        "/service",
        json={
            "slotid": 1,
            "servicetype": ServiceType.ELECTRICIAN,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_book_service_http_exception(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.book_service",
        side_effect=HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Slot already booked",
        ),
    )

    response = client.post(
        "/service",
        json={
            "slotid": 5,
            "servicetype": ServiceType.PLUMBER,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Slot already booked"


def test_book_service_internal_error(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.book_service",
        side_effect=Exception("DB down"),
    )

    response = client.post(
        "/service",
        json={
            "slotid": 2,
            "servicetype": ServiceType.ELECTRICIAN,
        },
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_book_service_missing_slotid(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.post(
        "/service",
        json={
            "servicetype": ServiceType.PLUMBER,
        },
    )

    assert response.status_code == 422


def test_book_service_extra_field(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.post(
        "/service",
        json={
            "slotid": 1,
            "servicetype": ServiceType.PLUMBER,
            "extra": "not_allowed",
        },
    )

    assert response.status_code == 422


def test_book_service_invalid_service_type(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.post(
        "/service",
        json={
            "slotid": 1,
            "servicetype": "CARPENTER",
        },
    )

    assert response.status_code == 422


def test_cancel_service_request_success(client, mocker, override_jwt):
    request_id = uuid4()
    user_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=user_id)

    fake_request = ServiceRequest.model_construct(
        id=request_id,
        resident_id=user_id,
        status=Status.STATUSPENDING,
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_request_by_id",
        return_value=fake_request,
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.delete_request",
        return_value=None,
    )

    response = client.delete(f"/service/cancel/{request_id}")

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Request cancelled successfully"
    assert body["data"] is None


def test_cancel_service_request_unauthorized(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=uuid4())

    fake_request = ServiceRequest.model_construct(
        id=request_id,
        resident_id=uuid4(),
        status=Status.STATUSPENDING,
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_request_by_id",
        return_value=fake_request,
    )

    response = client.delete(f"/service/cancel/{request_id}")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized Access"


def test_cancel_service_request_not_pending(client, mocker, override_jwt):
    request_id = uuid4()
    user_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=user_id)

    fake_request = ServiceRequest.model_construct(
        id=request_id,
        resident_id=user_id,
        status=Status.STATUSAPPROVED,
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_request_by_id",
        return_value=fake_request,
    )

    response = client.delete(f"/service/cancel/{request_id}")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Only pending requests can be cancelled"


def test_cancel_service_request_http_exception(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=uuid4())

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_request_by_id",
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Service request not found",
        ),
    )

    response = client.delete(f"/service/cancel/{request_id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Service request not found"
    

def test_cancel_service_request_internal_error(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=uuid4())

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_request_by_id",
        side_effect=Exception("DB down"),
    )

    response = client.delete(f"/service/cancel/{request_id}")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_cancel_service_request_invalid_uuid(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT, user_id=uuid4())

    response = client.delete("/service/cancel/not-a-uuid")

    assert response.status_code == 422


def test_reschedule_service_request_success(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.reschedule_request",
        return_value=None,
    )

    response = client.patch(
        f"/service/reschedule/{request_id}",
        json={"slotid": 5},
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Service request rescheduled successfully"
    assert body["data"] is None


def test_reschedule_service_request_unauthorized(client, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEADMIN)

    response = client.patch(
        f"/service/reschedule/{request_id}",
        json={"slotid": 5},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_reschedule_service_request_http_exception(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.reschedule_request",
        side_effect=HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Slot already booked",
        ),
    )

    response = client.patch(
        f"/service/reschedule/{request_id}",
        json={"slotid": 5},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Slot already booked"
