import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from internal.service.feedback_service import FeedbackService
from internal.models.user import User, UserRole
from internal.models.service_request import ServiceRequest, Status, ServiceType
from internal.models.feedback import Feedback

@pytest.mark.asyncio
async def test_post_feedback_success(mocker):
    service = FeedbackService()
    
    user = User.model_construct(id="1", first_name="John", middle_name="", last_name="Doe", flat="101", email="john@example.com", password="hashed", role=UserRole.ROLERESIDENT)
    request_obj = ServiceRequest.model_construct(request_id="req1", resident_id="1", flat="101", service_type=ServiceType.PLUMBER, assigned_to="officer1", date="2025-01-01", time_slot="09:00-09:45", status=Status.STATUSPENDING)
    
    mocker.patch.object(
        service.feedback_repository,
        "is_feedback_present",
        new_callable=AsyncMock,
        return_value=False
    )
    
    mocker.patch.object(
        service.feedback_repository,
        "post_feedback",
        new_callable=AsyncMock,
        return_value=None
    )
    
    await service.post_feedback(user, request_obj, rating=5, content="Great service")
    
    service.feedback_repository.is_feedback_present.assert_awaited_once_with("req1")
    service.feedback_repository.post_feedback.assert_awaited_once()
    
@pytest.mark.asyncio
async def test_post_feedback_already_exists(mocker):
    service = FeedbackService()
    
    user = User.model_construct(id="1", first_name="John", middle_name="", last_name="Doe", flat="101", email="john@example.com", password="hashed", role=UserRole.ROLERESIDENT)
    request_obj = ServiceRequest.model_construct(request_id="req1", resident_id="1", flat="101", service_type=ServiceType.PLUMBER, assigned_to="officer1", date="2025-01-01", time_slot="09:00-09:45", status=Status.STATUSPENDING)
    
    mocker.patch.object(
        service.feedback_repository,
        "is_feedback_present",
        new_callable=AsyncMock,
        return_value=True
    )
    
    with pytest.raises(HTTPException) as exc:
        await service.post_feedback(user, request_obj, rating=5, content="Great service")
        
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "Feedback is already given"

@pytest.mark.asyncio
async def test_post_feedback_generic_exception(mocker):
    service = FeedbackService()
    
    user = User.model_construct(id="1", first_name="John", middle_name="", last_name="Doe", flat="101", email="john@example.com", password="hashed", role=UserRole.ROLERESIDENT)
    request_obj = ServiceRequest.model_construct(request_id="req1", resident_id="1", flat="101", service_type=ServiceType.PLUMBER, assigned_to="officer1", date="2025-01-01", time_slot="09:00-09:45", status=Status.STATUSPENDING)
    
    mocker.patch.object(
        service.feedback_repository,
        "is_feedback_present",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )
    
    with pytest.raises(Exception) as exc:
        await service.post_feedback(user, request_obj, rating=5, content="Great service")
    
    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_get_all_feedbacks_success(mocker):
    service = FeedbackService()
    
    fake_feedbacks = [
        Feedback.model_construct(resident_id="1", flat="101", rating=5, content="Good", name="John Doe", request_id="req1", assignedto="officer1", servicetype="PLUMBER", date="2025-01-01", timeslot="09:00-09:45"),
        Feedback.model_construct(resident_id="2", flat="102", rating=4, content="Okay", name="Jane Doe", request_id="req2", assignedto="officer2", servicetype="ELECTRICIAN", date="2025-01-02", timeslot="10:00-10:45"),
    ]
    
    mocker.patch.object(
        service.feedback_repository,
        "get_all_feedbacks",
        new_callable=AsyncMock,
        return_value=fake_feedbacks
    )
    
    result = await service.get_all_feedbacks()
    assert result == fake_feedbacks
    assert len(result) == 2

@pytest.mark.asyncio
async def test_get_all_feedbacks_http_exception(mocker):
    service = FeedbackService()
    
    mocker.patch.object(
        service.feedback_repository,
        "get_all_feedbacks",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=400, detail="Bad request")
    )
    
    with pytest.raises(HTTPException) as exc:
        await service.get_all_feedbacks()
    
    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad request"

@pytest.mark.asyncio
async def test_get_all_feedbacks_generic_exception(mocker):
    service = FeedbackService()
    
    mocker.patch.object(
        service.feedback_repository,
        "get_all_feedbacks",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )
    
    with pytest.raises(Exception) as exc:
        await service.get_all_feedbacks()
    
    assert str(exc.value) == "DB down"
