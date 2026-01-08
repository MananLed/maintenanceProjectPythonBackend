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


def test_reschedule_service_request_internal_error(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.reschedule_request",
        side_effect=Exception("DB down"),
    )

    response = client.patch(
        f"/service/reschedule/{request_id}",
        json={"slotid": 5},
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_reschedule_service_request_invalid_uuid(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.patch(
        "/service/reschedule/not-a-uuid",
        json={"slotid": 5},
    )

    assert response.status_code == 422


def test_reschedule_service_request_invalid_body(client, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.patch(
        f"/service/reschedule/{request_id}",
        json={},  
    )

    assert response.status_code == 422


def test_approve_request_success(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.update_request_status",
        return_value=None,
    )

    response = client.patch(
        f"/service/approve/{request_id}",
        json={"assignedto": "officer@example.com"}
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Request approved successfully"
    assert body["data"] is None


def test_approve_request_unauthorized(client, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.patch(
        f"/service/approve/{request_id}",
        json={"assigned_to": "officer@example.com"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_approve_request_http_exception(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEOFFICER)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.update_request_status",
        side_effect=HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Request cannot be approved"
        )
    )

    response = client.patch(
        f"/service/approve/{request_id}",
        json={"assignedto": "officer@example.com"}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Request cannot be approved"


def test_approve_request_internal_error(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.update_request_status",
        side_effect=Exception("DB down")
    )

    response = client.patch(
        f"/service/approve/{request_id}",
        json={"assignedto": "officer@example.com"}
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_approve_request_invalid_uuid(client, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    response = client.patch(
        "/service/approve/not-a-uuid",
        json={"assignedto": "officer@example.com"}
    )

    assert response.status_code == 422


def test_approve_request_invalid_body(client, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEADMIN)

    response = client.patch(
        f"/service/approve/{request_id}",
        json={}  
    )

    assert response.status_code == 422


def test_complete_request_success(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.update_request_status",
        return_value=None,
    )

    response = client.patch(f"/service/complete/{request_id}")

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Request marked completed successfully"
    assert body["data"] is None


def test_complete_request_unauthorized(client, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.patch(f"/service/complete/{request_id}")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_complete_request_http_exception(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEOFFICER)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.update_request_status",
        side_effect=HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Cannot complete request"
        )
    )

    response = client.patch(f"/service/complete/{request_id}")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Cannot complete request"


def test_complete_request_internal_error(client, mocker, override_jwt):
    request_id = uuid4()

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.update_request_status",
        side_effect=Exception("DB down")
    )

    response = client.patch(f"/service/complete/{request_id}")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_complete_request_invalid_uuid(client, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    response = client.patch("/service/complete/not-a-uuid")

    assert response.status_code == 422


def test_get_all_requests_success(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    fake_request = ServiceRequest.model_construct(

    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=[
            [fake_request], 
            [fake_request], 
            [fake_request], 
            [fake_request],  
            [fake_request],  
            [fake_request],  
        ]
    )

    response = client.get("/service/all")

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "All requests fetched successfully"
    data = body["data"]
    assert "Pending" in data
    assert "Approved" in data
    assert "Completed" in data
    assert len(data["Pending"]) == 2
    assert len(data["Approved"]) == 2
    assert len(data["Completed"]) == 2


def test_get_all_requests_unauthorized(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.get("/service/all")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_get_all_requests_http_exception(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEOFFICER)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=HTTPException(status_code=400, detail="Something went wrong")
    )

    response = client.get("/service/all")

    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Something went wrong"


def test_get_all_requests_internal_error(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=Exception("DB down")
    )

    response = client.get("/service/all")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_all_requests_http_exception(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEOFFICER)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=HTTPException(status_code=400, detail="Something went wrong")
    )

    response = client.get("/service/all")

    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Something went wrong"


def test_get_all_requests_internal_error(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=Exception("DB down")
    )

    response = client.get("/service/all")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_all_requests_of_resident_success(client, mocker, override_jwt):
    resident_id = str(uuid4())

    override_jwt(
        role=UserRole.ROLERESIDENT,
        user_id=resident_id
    )

    fake_request = ServiceRequest.model_construct(
        
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=[
            [fake_request],  
            [fake_request], 
            [fake_request], 
            [fake_request], 
            [fake_request],  
            [fake_request],
        ],
    )

    response = client.get("/service/resident/all")

    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "All requests fetched successfully"

    data = body["data"]
    assert len(data["Pending"]) == 2
    assert len(data["Approved"]) == 2
    assert len(data["Completed"]) == 2


def test_get_all_requests_of_resident_http_exception(client, mocker, override_jwt):
    override_jwt(
        role=UserRole.ROLERESIDENT,
        user_id="resident-123"
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid request"
        ),
    )

    response = client.get("/service/resident/all")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Invalid request"


def test_get_all_requests_of_resident_internal_error(client, mocker, override_jwt):
    override_jwt(
        role=UserRole.ROLERESIDENT,
        user_id="resident-123"
    )

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=Exception("DB down"),
    )

    response = client.get("/service/resident/all")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_requests_by_type_status_admin_success(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    fake_request = ServiceRequest.model_construct(
        id=uuid4(),
        resident_id=str(uuid4()),
        status=Status.STATUSPENDING,
        service_type=ServiceType.PLUMBER,
        slot_id=1
    )

    mock = mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        return_value=[fake_request],
    )

    response = client.get(
        f"/service/type-status?status={Status.STATUSPENDING.value}&serviceType={ServiceType.PLUMBER.value}"
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Requests fetched successfully"
    assert len(body["data"]) == 1

    mock.assert_awaited_once_with(ServiceType.PLUMBER, Status.STATUSPENDING)


def test_get_requests_by_type_status_officer_success(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEOFFICER)

    mock = mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        return_value=[],
    )

    response = client.get(
        f"/service/type-status?status={Status.STATUSAPPROVED.value}&serviceType={ServiceType.ELECTRICIAN.value}"
    )

    assert response.status_code == HTTPStatus.OK

    mock.assert_awaited_once_with(
        ServiceType.ELECTRICIAN,
        Status.STATUSAPPROVED
    )


def test_get_requests_by_type_status_resident_success(client, mocker, override_jwt):
    resident_id = "resident-123"

    override_jwt(
        role=UserRole.ROLERESIDENT,
        user_id=resident_id
    )

    mock = mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        return_value=[],
    )

    response = client.get(
        f"/service/type-status?status={Status.STATUSCOMPLETED.value}&serviceType={ServiceType.PLUMBER.value}"
    )

    assert response.status_code == HTTPStatus.OK

    mock.assert_awaited_once_with(
        ServiceType.PLUMBER,
        Status.STATUSCOMPLETED,
        resident_id
    )


def test_get_requests_by_type_status_http_exception(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Requests not found"
        ),
    )

    response = client.get(
        f"/service/type-status?status={Status.STATUSPENDING.value}&serviceType={ServiceType.PLUMBER.value}"
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Requests not found"


def test_get_requests_by_type_status_internal_error(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_requests_by_type_and_status",
        side_effect=Exception("DB down"),
    )

    response = client.get(
        f"/service/type-status?status={Status.STATUSPENDING.value}&serviceType={ServiceType.PLUMBER.value}"
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_available_time_slots_success(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLERESIDENT)

    mock_slots = [
        {"StartTime": "df", "EndTime": "dsfdsfd", "Label": "dfdffd"},
    ]

    mock = mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_available_time_slots",
        return_value=mock_slots,
    )

    response = client.get(
        f"/service/time-slots?serviceType={ServiceType.PLUMBER.value}"
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Available time slots fetched successfully"
    assert body["data"] == mock_slots

    mock.assert_awaited_once_with(ServiceType.PLUMBER)


def test_get_available_time_slots_http_exception(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_available_time_slots",
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No slots available"
        ),
    )

    response = client.get(
        f"/service/time-slots?serviceType={ServiceType.ELECTRICIAN.value}"
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "No slots available"


def test_get_available_time_slots_internal_error(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLERESIDENT)

    mocker.patch(
        "internal.handler.request_handler.request_service_instance.get_available_time_slots",
        side_effect=Exception("DB down"),
    )

    response = client.get(
        f"/service/time-slots?serviceType={ServiceType.PLUMBER.value}"
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_available_time_slots_invalid_service_type(client, override_jwt):

    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.get(
        "/service/time-slots?serviceType=INVALID"
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
