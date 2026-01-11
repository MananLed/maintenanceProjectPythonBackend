from uuid import uuid4
from internal.models.user import User, UserRole
from internal.models.service_request import ServiceRequest, Status
from unittest.mock import AsyncMock
from internal.constants.constants import *

def test_post_feedback_success(client, mocker, override_jwt):
    user_id = uuid4()
    request_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=str(user_id))

    user = User.model_construct(
        id=user_id,
        role=UserRole.ROLERESIDENT
    )

    service_request = ServiceRequest.model_construct(
        resident_id=user_id,
        status=Status.STATUSCOMPLETED
    )

    mocker.patch(
        "internal.handler.feedback_handler.user_service_instance.get_user_by_id_and_role",
        AsyncMock(return_value=user)
    )

    mocker.patch(
        "internal.handler.feedback_handler.request_service_instance.get_request_by_id",
        AsyncMock(return_value=service_request)
    )

    post_feedback_mock = AsyncMock()
    mocker.patch(
        "internal.handler.feedback_handler.feedback_service_instance.post_feedback",
        post_feedback_mock
    )

    payload = {
        "request_id": str(request_id),
        "rating": 5,
        "content": "Great service"
    }

    response = client.post("/feedbacks/request", json=payload)

    assert response.status_code == 201
    assert response.json()["message"] == "Feedback posted successfully"

    post_feedback_mock.assert_called_once_with(
        user,
        service_request,
        5,
        "Great service"
    )


def test_post_feedback_user_not_owner(client, mocker, override_jwt):
    user = User.model_construct(
        id=uuid4(),
        role=UserRole.ROLERESIDENT
    )

    override_jwt(role=UserRole.ROLERESIDENT, user_id=str(uuid4()))

    service_request = ServiceRequest.model_construct(
        resident_id=uuid4(),
        status=Status.STATUSCOMPLETED
    )

    mocker.patch(
        "internal.handler.feedback_handler.user_service_instance.get_user_by_id_and_role",
        AsyncMock(return_value=user)
    )

    mocker.patch(
        "internal.handler.feedback_handler.request_service_instance.get_request_by_id",
        AsyncMock(return_value=service_request)
    )

    payload = {
        "request_id": str(uuid4()),
        "rating": 4,
        "content": "Good"
    }

    response = client.post("/feedbacks/request", json=payload)

    assert response.status_code == 401
    assert response.json()["errorcode"] == FEEDBACK_001

def test_post_feedback_request_not_completed(client, mocker, override_jwt):
    user_id = uuid4()

    override_jwt(role=UserRole.ROLERESIDENT, user_id=str(user_id))

    user = User.model_construct(
        id=user_id,
        role=UserRole.ROLERESIDENT
    )

    service_request = ServiceRequest.model_construct(
        resident_id=user_id,
        status=Status.STATUSAPPROVED
    )

    mocker.patch(
        "internal.handler.feedback_handler.user_service_instance.get_user_by_id_and_role",
        AsyncMock(return_value=user)
    )

    mocker.patch(
        "internal.handler.feedback_handler.request_service_instance.get_request_by_id",
        AsyncMock(return_value=service_request)
    )

    payload = {
        "request_id": str(uuid4()),
        "rating": 3,
        "content": "Okay"
    }

    response = client.post("/feedbacks/request", json=payload)

    assert response.status_code == 400
    assert response.json()["errorcode"] == FEEDBACK_002

