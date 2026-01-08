import pytest
from unittest.mock import AsyncMock
from internal.service.society_service import SocietyService
from internal.models.user import User, UserRole
from fastapi import HTTPException, status


@pytest.mark.asyncio
async def test_get_all_users_by_role_success(mocker):
    service = SocietyService()

    fake_users = [
        User.model_construct(
            id="1",
            first_name="John",
            middle_name="",
            last_name="Doe",
            mobile_number="9876543210",
            email="john@example.com",
            flat="101",
            password="hashed",
            role=UserRole.ROLERESIDENT,
        )
    ]

    mocker.patch(
        "internal.service.society_service.society_repository_instance.get_all_users_by_role",
        new_callable=AsyncMock,
        return_value=fake_users,
    )

    result = await service.get_all_users_by_role(UserRole.ROLERESIDENT)
    assert result == fake_users


@pytest.mark.asyncio
async def test_get_all_users_by_role_http_exception(mocker):
    service = SocietyService()

    mocker.patch(
        "internal.service.society_service.society_repository_instance.get_all_users_by_role",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"),
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_all_users_by_role(UserRole.ROLERESIDENT)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Role not found"


@pytest.mark.asyncio
async def test_get_all_users_by_role_generic_exception(mocker):
    service = SocietyService()

    mocker.patch(
        "internal.service.society_service.society_repository_instance.get_all_users_by_role",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    with pytest.raises(Exception) as exc:
        await service.get_all_users_by_role(UserRole.ROLERESIDENT)

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_delete_user_success(mocker):
    service = SocietyService()

    mock_delete = mocker.patch(
        "internal.service.society_service.society_repository_instance.delete_user",
        new_callable=AsyncMock,
        return_value=None,
    )

    await service.delete_user("some-uuid", UserRole.ROLEOFFICER)
    mock_delete.assert_awaited_once_with("some-uuid", UserRole.ROLEOFFICER)


@pytest.mark.asyncio
async def test_delete_user_http_exception(mocker):
    service = SocietyService()

    mocker.patch(
        "internal.service.society_service.society_repository_instance.delete_user",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=404, detail="Officer not found"),
    )

    with pytest.raises(HTTPException) as exc:
        await service.delete_user("some-uuid", UserRole.ROLEOFFICER)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Officer not found"


@pytest.mark.asyncio
async def test_delete_user_generic_exception(mocker):
    service = SocietyService()

    mocker.patch(
        "internal.service.society_service.society_repository_instance.delete_user",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    with pytest.raises(Exception) as exc:
        await service.delete_user("some-uuid", UserRole.ROLEOFFICER)

    assert str(exc.value) == "DB down"
