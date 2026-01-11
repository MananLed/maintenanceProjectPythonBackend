import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from internal.repository.notice_repository import NoticeRepository
from internal.models.notice import Notice
from internal.errors.base_exception import AppException
from internal.constants.constants import *
import uuid

@pytest.fixture
def fake_deserializer():
    class FakeDeserializer:
        def deserialize(self, value):
            return list(value.values())[0]
    return FakeDeserializer

@pytest.mark.asyncio
async def test_issue_notice_success(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {}

    repo = NoticeRepository(
        ddb_connection=dynamodb,
        table_name="NoticeTable",
        deserializer=fake_deserializer,
    )

    notice = Notice.model_construct(
        id="123",
        content="Test notice",
        date_issued=datetime.now(timezone.utc),
        month=9,
        year=2025,
    )

    await repo.issue_notice(notice)

    dynamodb.execute_statement.assert_called_once()

@pytest.mark.asyncio
async def test_issue_notice_db_exception(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DynamoDB down")

    repo = NoticeRepository(
        ddb_connection=dynamodb,
        table_name="NoticeTable",
        deserializer=fake_deserializer,
    )

    notice = Notice.model_construct(
        id="123",
        content="Test notice",
        date_issued=datetime.now(timezone.utc),
        month=9,
        year=2025,
    )

    with pytest.raises(AppException) as exc:
        await repo.issue_notice(notice)

    assert exc.value.error_code == NOTICE_001
    assert exc.value.status_code == 500

@pytest.fixture
def fake_deserializer():
    class FakeDeserializer:
        def deserialize(self, value):
            return list(value.values())[0]
    return FakeDeserializer

@pytest.mark.asyncio
async def test_get_all_notices_success(fake_deserializer):
    dynamodb = MagicMock()

    item_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "id": {"S": item_id},
                "content": {"S": "Notice 1"},
                "date_issued": {"S": now_str},
                "month": {"S": "1"},
                "year": {"N": "2025"}
            },
            {
                "id": {"S": str(uuid.uuid4())},
                "content": {"S": "Notice 2"},
                "date_issued": {"S": now_str},
                "month": {"S": "2"},
                "year": {"N": "2025"}
            }
        ]
    }

    repo = NoticeRepository(
        ddb_connection=dynamodb,
        table_name="NoticeTable",
        deserializer=fake_deserializer,
    )

    notices = await repo.get_all_notices()

    assert len(notices) == 2
    assert all(isinstance(n, Notice) for n in notices)
    assert notices[0].content == "Notice 1"
    assert notices[1].content == "Notice 2"

@pytest.mark.asyncio
async def test_get_all_notices_db_failure(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DB down")

    repo = NoticeRepository(
        ddb_connection=dynamodb,
        table_name="NoticeTable",
        deserializer=fake_deserializer,
    )

    with pytest.raises(AppException) as exc:
        await repo.get_all_notices()

    assert exc.value.error_code == NOTICE_002
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_get_all_notices_by_month_and_year_success_month(fake_deserializer):
    dynamodb = MagicMock()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    item_id = str(uuid.uuid4())

    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "id": {"S": item_id},
                "content": {"S": "Monthly Notice"},
                "date_issued": {"S": now_str},
                "month": {"S": "5"},
                "year": {"N": "2025"}
            }
        ]
    }

    repo = NoticeRepository(dynamodb, "NoticeTable", fake_deserializer)
    notices = await repo.get_all_notices_by_month_and_year(2025, 5)

    assert len(notices) == 1
    assert notices[0].content == "Monthly Notice"
    assert notices[0].month == 5
    assert notices[0].year == 2025


@pytest.mark.asyncio
async def test_get_all_notices_by_month_and_year_success_year_only(fake_deserializer):
    dynamodb = MagicMock()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    item_id = str(uuid.uuid4())

    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "id": {"S": item_id},
                "content": {"S": "Yearly Notice"},
                "date_issued": {"S": now_str},
                "month": {"S": "1"},
                "year": {"N": "2025"}
            }
        ]
    }

    repo = NoticeRepository(dynamodb, "NoticeTable", fake_deserializer)
    notices = await repo.get_all_notices_by_month_and_year(2025)

    assert len(notices) == 1
    assert notices[0].content == "Yearly Notice"
    assert notices[0].year == 2025


@pytest.mark.asyncio
async def test_get_all_notices_by_month_and_year_failure(fake_deserializer):
    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DB down")

    repo = NoticeRepository(dynamodb, "NoticeTable", fake_deserializer)

    with pytest.raises(AppException) as exc:
        await repo.get_all_notices_by_month_and_year(2025, 5)

    assert exc.value.error_code == NOTICE_003
    assert exc.value.status_code == 500
