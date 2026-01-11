import pytest
from unittest.mock import MagicMock
import uuid
from internal.repository.feedback_repository import FeedbackRepository
from internal.models.feedback import Feedback
from internal.errors.base_exception import AppException
from internal.constants.constants import *

@pytest.fixture
def fake_deserializer():
    class FakeDeserializer:
        def deserialize(self, value):
            return list(value.values())[0]
    return FakeDeserializer

@pytest.mark.asyncio
async def test_get_all_feedbacks_success(fake_deserializer):
    dynamodb = MagicMock()

    feedback_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "id": {"S": feedback_id},
                "resident_id": {"S": "user123"},
                "flat_no": {"S": "101"},
                "rating": {"N": "5"},
                "content": {"S": "Great service!"},
                "username": {"S": "John Doe"},
                "request_id": {"S": request_id},
                "assigned_to": {"S": "officer1"},
                "service_type": {"S": "PLUMBER"},
                "date": {"S": "10-01-2026"},
                "time_slot": {"S": "10:00-10:45"}
            }
        ]
    }

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)
    feedbacks = await repo.get_all_feedbacks()

    assert len(feedbacks) == 1
    assert isinstance(feedbacks[0], Feedback)
    assert feedbacks[0].resident_id == "user123"
    assert feedbacks[0].flat == "101"
    assert feedbacks[0].rating == 5
    assert feedbacks[0].content == "Great service!"
    assert feedbacks[0].service_type == "PLUMBER"

@pytest.mark.asyncio
async def test_get_all_feedbacks_failure(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DB down")

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.get_all_feedbacks()

    assert exc.value.error_code == FEEDBACK_004
    assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_is_feedback_present_true(fake_deserializer):
    dynamodb = MagicMock()
    request_id = uuid.uuid4()

    dynamodb.execute_statement.return_value = {
        "Items": [
            {"id": {"S": str(uuid.uuid4())}}
        ]
    }

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)
    result = await repo.is_feedback_present(request_id)

    assert result is True

@pytest.mark.asyncio
async def test_is_feedback_present_false(fake_deserializer):
    dynamodb = MagicMock()
    request_id = uuid.uuid4()

    dynamodb.execute_statement.return_value = {"Items": []}

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)
    result = await repo.is_feedback_present(request_id)

    assert result is False

@pytest.mark.asyncio
async def test_is_feedback_present_exception(fake_deserializer):
    dynamodb = MagicMock()
    request_id = uuid.uuid4()

    dynamodb.execute_statement.side_effect = Exception("DB down")

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.is_feedback_present(request_id)

    assert exc.value.error_code == FEEDBACK_005
    assert exc.value.status_code == 500

@pytest.fixture
def feedback_sample():
    return Feedback.model_construct(
        resident_id="resident-123",
        flat="101",
        rating=5,
        content="Great service",
        name="John Doe",
        resident_name="John Doe",
        request_id=uuid.uuid4(),
        assigned_to="officer-1",
        service_type="PLUMBER",
        date="2026-01-11",
        time_slot="09:00-09:45",
        id=uuid.uuid4()
    )

@pytest.mark.asyncio
async def test_post_feedback_success(fake_deserializer, feedback_sample):
    dynamodb = MagicMock()
    
    dynamodb.execute_transaction.return_value = None

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)

    result = await repo.post_feedback(feedback_sample)

    assert result is None

    dynamodb.execute_transaction.assert_called_once()


@pytest.mark.asyncio
async def test_post_feedback_exception(fake_deserializer, feedback_sample):
    dynamodb = MagicMock()
    
    dynamodb.execute_transaction.side_effect = Exception("DB down")

    repo = FeedbackRepository(dynamodb, "FeedbackTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.post_feedback(feedback_sample)

    assert exc.value.error_code == FEEDBACK_006
    assert exc.value.status_code == 500
