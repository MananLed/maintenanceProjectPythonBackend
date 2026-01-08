import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from datetime import datetime, timezone
from internal.service.notice_service import NoticeService
from internal.dto.notice import NoticeInput
from internal.models.notice import Notice

@pytest.mark.asyncio
async def test_issue_notice_success(mocker):
    service = NoticeService()

    notice_input = NoticeInput(
        content="Test notice content"
    )

    mock_repo = mocker.patch(
        "internal.service.notice_service.notice_repository_instance.issue_notice",
        new_callable=AsyncMock,
        return_value=None
    )

    await service.issue_notice(notice_input)

    assert mock_repo.await_count == 1
    called_notice = mock_repo.await_args[0][0]
    assert isinstance(called_notice, Notice)
    assert called_notice.content == "Test notice content"
    assert isinstance(called_notice.date_issued, datetime)
    assert called_notice.month == called_notice.date_issued.month
    assert called_notice.year == called_notice.date_issued.year

@pytest.mark.asyncio
async def test_issue_notice_http_exception(mocker):
    service = NoticeService()
    notice_input = NoticeInput(content="Test notice content")

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.issue_notice",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=400, detail="Bad request")
    )

    with pytest.raises(HTTPException) as exc:
        await service.issue_notice(notice_input)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad request"

@pytest.mark.asyncio
async def test_issue_notice_generic_exception(mocker):
    service = NoticeService()
    notice_input = NoticeInput(content="Test notice content")

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.issue_notice",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )

    with pytest.raises(Exception) as exc:
        await service.issue_notice(notice_input)

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_get_all_notices_success(mocker):
    service = NoticeService()

    fake_notices = [
        Notice.model_construct(id="1", content="Notice 1", date_issued=datetime.now(timezone.utc), month=1, year=2025),
        Notice.model_construct(id="2", content="Notice 2", date_issued=datetime.now(timezone.utc), month=1, year=2025),
    ]

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.get_all_notices",
        new_callable=AsyncMock,
        return_value=fake_notices
    )

    notices = await service.get_all_notices()
    assert notices == fake_notices
    assert len(notices) == 2
    assert all(isinstance(n, Notice) for n in notices)

@pytest.mark.asyncio
async def test_get_all_notices_http_exception(mocker):
    service = NoticeService()

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.get_all_notices",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=400, detail="Bad request")
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_all_notices()

    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad request"

@pytest.mark.asyncio
async def test_get_all_notices_generic_exception(mocker):
    service = NoticeService()

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.get_all_notices",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )

    with pytest.raises(Exception) as exc:
        await service.get_all_notices()

    assert str(exc.value) == "DB down"

@pytest.mark.asyncio
async def test_get_all_notices_by_month_and_year_success(mocker):
    service = NoticeService()
    year, month = 2025, 5

    fake_notices = [
        Notice.model_construct(id="1", content="Notice 1", date_issued=datetime.now(timezone.utc), month=month, year=year),
    ]

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.get_all_notices_by_month_and_year",
        new_callable=AsyncMock,
        return_value=fake_notices
    )

    notices = await service.get_all_notices_by_month_and_year(year, month)
    assert notices == fake_notices
    assert len(notices) == 1
    assert all(isinstance(n, Notice) for n in notices)

@pytest.mark.asyncio
async def test_get_all_notices_by_month_and_year_http_exception(mocker):
    service = NoticeService()
    year, month = 2025, 5

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.get_all_notices_by_month_and_year",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=400, detail="Bad request")
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_all_notices_by_month_and_year(year, month)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad request"

@pytest.mark.asyncio
async def test_get_all_notices_by_month_and_year_generic_exception(mocker):
    service = NoticeService()
    year, month = 2025, 5

    mocker.patch(
        "internal.service.notice_service.notice_repository_instance.get_all_notices_by_month_and_year",
        new_callable=AsyncMock,
        side_effect=Exception("DB down")
    )

    with pytest.raises(Exception) as exc:
        await service.get_all_notices_by_month_and_year(year, month)

    assert str(exc.value) == "DB down"


