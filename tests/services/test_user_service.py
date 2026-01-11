import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from internal.errors.base_exception import AppException
from internal.constants.constants import *
from internal.service.user_service import UserService
from internal.dto.user import ChangePassword, LoginInput, SignInInput
from internal.models.user import UserRole, User
from uuid import uuid4

@pytest.fixture
def sign_in_input():
    return SignInInput.model_construct(
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="Strong@123",
    )


@pytest.mark.asyncio
async def test_change_password_old_password_mismatch(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        return_value=False,
    )

    change_input = ChangePassword(
        oldPassword="wrongOld",
        newPassword="NewPass@12345",
    )

    with pytest.raises(HTTPException) as exc:
        await service.change_password(
            change_input,
            current_password="hashed-password",
            role="USER",
            email="test@example.com",
            user_id="123",
        )

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Old password does'nt match"


@pytest.mark.asyncio
async def test_change_password_no_change(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        side_effect=[True, True], 
    )

    change_input = ChangePassword(
        oldPassword="OldPass@12345",
        newPassword="OldPass@12345",
    )

    with pytest.raises(HTTPException) as exc:
        await service.change_password(
            change_input,
            current_password="hashed-password",
            role="USER",
            email="test@example.com",
            user_id="123",
        )

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "No change in the password"


@pytest.mark.asyncio
async def test_change_password_success(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        side_effect=[True, False],  
    )

    mocker.patch(
        "internal.service.user_service.generate_hash_from_password",
        return_value="new-hashed-password",
    )

    repo_mock = mocker.patch(
        "internal.service.user_service.user_repository_instance.change_password",
        new_callable=AsyncMock,
    )

    change_input = ChangePassword(
        oldPassword="OldPass@12345",
        newPassword="NewPass@12345",
    )

    await service.change_password(
        change_input,
        current_password="hashed-password",
        role="USER",
        email="test@example.com",
        user_id="123",
    )

    repo_mock.assert_awaited_once_with(
        "new-hashed-password",
        "USER",
        "test@example.com",
        "123",
    )


@pytest.mark.asyncio
async def test_change_password_repository_http_exception(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        side_effect=[True, False],
    )

    mocker.patch(
        "internal.service.user_service.generate_hash_from_password",
        return_value="hashed",
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.change_password",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    change_input = ChangePassword(
        oldPassword="OldPass@12345",
        newPassword="NewPass@12345",
    )

    with pytest.raises(HTTPException) as exc:
        await service.change_password(
            change_input,
            current_password="hashed-password",
            role="USER",
            email="test@example.com",
            user_id="123",
        )

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_change_password_repository_exception(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        side_effect=[True, False],
    )

    mocker.patch(
        "internal.service.user_service.generate_hash_from_password",
        return_value="hashed",
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.change_password",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    change_input = ChangePassword(
        oldPassword="OldPass@12345",
        newPassword="NewPass@12345",
    )

    with pytest.raises(Exception) as exc:
        await service.change_password(
            change_input,
            current_password="hashed-password",
            role="USER",
            email="test@example.com",
            user_id="123",
        )

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_get_user_by_email_and_password_success(mocker):
    service = UserService()

    fake_user = User.model_construct(
        id="123",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed-password",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        return_value=fake_user,
    )

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        return_value=True,
    )

    mocker.patch(
        "internal.service.user_service.create_jwt_token",
        return_value="fake-jwt-token",
    )

    login_input = LoginInput(
        email="test@example.com",
        password="Password@123",
    )

    result = await service.get_user_by_email_and_password(login_input)

    assert result == {
        "token": "fake-jwt-token",
        "email": "test@example.com",
        "role": UserRole.ROLERESIDENT,
    }


@pytest.mark.asyncio
async def test_get_user_by_email_and_password_invalid_password(mocker):
    service = UserService()

    fake_user = User.model_construct(
        id="123",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed-password",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        return_value=fake_user,
    )

    mocker.patch(
        "internal.service.user_service.compare_hash_and_password",
        return_value=False,
    )

    login_input = LoginInput(
        email="test@example.com",
        password="WrongPassword",
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_user_by_email_and_password(login_input)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid Credentials"


@pytest.mark.asyncio
async def test_get_user_by_email_and_password_repo_http_exception(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    login_input = LoginInput(
        email="missing@example.com",
        password="Password@123",
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_user_by_email_and_password(login_input)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_user_by_email_and_password_repo_exception(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    login_input = LoginInput(
        email="test@example.com",
        password="Password@123",
    )

    with pytest.raises(Exception) as exc:
        await service.get_user_by_email_and_password(login_input)

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_get_user_by_email_success(mocker):
    service = UserService()

    fake_user = User.model_construct(
        id="123",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed-password",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        return_value=fake_user,
    )

    result = await service.get_user_by_email("test@example.com")

    assert result == fake_user

@pytest.mark.asyncio
async def test_get_user_by_email_http_exception(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_user_by_email("missing@example.com")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_user_by_email_exception(mocker):
    service = UserService()

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_email",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    with pytest.raises(Exception) as exc:
        await service.get_user_by_email("test@example.com")

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_get_user_by_id_and_role_success(mocker):
    service = UserService()
    user_id = uuid4()

    fake_user = User.model_construct(
        id=user_id,
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed-password",
        role=UserRole.ROLEADMIN,
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_id_and_role",
        new_callable=AsyncMock,
        return_value=fake_user,
    )

    result = await service.get_user_by_id_and_role(UserRole.ROLEADMIN, user_id)

    assert result == fake_user


@pytest.mark.asyncio
async def test_get_user_by_id_and_role_http_exception(mocker):
    service = UserService()
    user_id = uuid4()

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_id_and_role",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await service.get_user_by_id_and_role(UserRole.ROLEOFFICER, user_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_user_by_id_and_role_exception(mocker):
    service = UserService()
    user_id = uuid4()

    mocker.patch(
        "internal.service.user_service.user_repository_instance.get_user_by_id_and_role",
        new_callable=AsyncMock,
        side_effect=Exception("Database error"),
    )

    with pytest.raises(Exception) as exc:
        await service.get_user_by_id_and_role(UserRole.ROLERESIDENT, user_id)

    assert str(exc.value) == "Database error"


@pytest.mark.asyncio
async def test_add_user_user_already_exists(mocker, sign_in_input):
    service = UserService()

    mocker.patch.object(
        service,
        "get_user_by_email",
        new_callable=AsyncMock,
        return_value=User.model_construct(
            id="1",
            first_name="Test",
            middle_name="",
            last_name="User",
            mobile_number="9876543210",
            email="test@example.com",
            flat="101",
            password="hashed",
            role=UserRole.ROLERESIDENT,
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await service.add_user(sign_in_input)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "User with given email already exists"


@pytest.mark.asyncio
async def test_add_user_success_resident(mocker, sign_in_input):
    service = UserService()

    mocker.patch.object(
        service,
        "get_user_by_email",
        new_callable=AsyncMock,
        side_effect=AppException(USER_003),
    )

    mock_add_user = mocker.patch(
        "internal.service.user_service.user_repository_instance.add_user",
        new_callable=AsyncMock,
    )

    await service.add_user(sign_in_input)

    mock_add_user.assert_called_once()


@pytest.mark.asyncio
async def test_add_user_success_officer(mocker, sign_in_input):
    service = UserService()

    mocker.patch.object(
        service,
        "get_user_by_email",
        new_callable=AsyncMock,
        side_effect=AppException(USER_003),
    )

    mock_add_user = mocker.patch(
        "internal.service.user_service.user_repository_instance.add_user",
        new_callable=AsyncMock,
    )

    await service.add_user(sign_in_input, is_officer=True)

    saved_user = mock_add_user.call_args[0][0]

    assert saved_user.role == UserRole.ROLEOFFICER
    assert saved_user.flat == "xxx"
    assert saved_user.mobile_number == "xxxxxxxxxx"


@pytest.mark.asyncio
async def test_add_user_password_hash_failure(mocker, sign_in_input):
    service = UserService()

    mocker.patch.object(
        service,
        "get_user_by_email",
        new_callable=AsyncMock,
        side_effect=AppException(USER_003),
    )

    mocker.patch(
        "internal.service.user_service.generate_hash_from_password",
        side_effect=Exception("Hashing failed"),
    )

    with pytest.raises(HTTPException) as exc:
        await service.add_user(sign_in_input)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.value.detail == "Internal Server Error"


@pytest.mark.asyncio
async def test_add_user_repository_http_exception(mocker, sign_in_input):
    service = UserService()

    mocker.patch.object(
        service,
        "get_user_by_email",
        new_callable=AsyncMock,
        side_effect=AppException(USER_003),
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.add_user",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status.HTTP_409_CONFLICT, detail="Duplicate entry"
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await service.add_user(sign_in_input)

    assert exc.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_add_user_repository_exception(mocker, sign_in_input):
    service = UserService()

    mocker.patch.object(
        service,
        "get_user_by_email",
        new_callable=AsyncMock,
        side_effect=AppException(USER_003),
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.add_user",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    with pytest.raises(Exception) as exc:
        await service.add_user(sign_in_input)

    assert str(exc.value) == "DB down"


@pytest.mark.asyncio
async def test_update_profile_success(mocker):
    service = UserService()

    user = User.model_construct(
        id="1",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed",
        role=UserRole.ROLERESIDENT,
    )

    mock_update = mocker.patch(
        "internal.service.user_service.user_repository_instance.update_profile",
        new_callable=AsyncMock,
        return_value=None,
    )

    await service.update_profile(user, old_email="old@example.com")

    mock_update.assert_awaited_once_with(user, "old@example.com")


@pytest.mark.asyncio
async def test_update_profile_http_exception(mocker):
    service = UserService()

    user = User.model_construct(
        id="1",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.update_profile",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await service.update_profile(user)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_update_profile_generic_exception(mocker):
    service = UserService()

    user = User.model_construct(
        id="1",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="hashed",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.service.user_service.user_repository_instance.update_profile",
        new_callable=AsyncMock,
        side_effect=Exception("DB down"),
    )

    with pytest.raises(Exception) as exc:
        await service.update_profile(user)

    assert str(exc.value) == "DB down"
