from unittest.mock import MagicMock
from internal.repository.user_repository import UserRepository
from internal.errors.base_exception import AppException
from internal.models.user import User, UserRole
from internal.constants.constants import *
import pytest
import uuid

@pytest.mark.asyncio
async def test_change_password_success(mocker):
    mock_dynamodb = MagicMock()
    mock_dynamodb.execute_transaction.return_value = None

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=MagicMock
    )

    await repo.change_password(
        new_password="hashed_pwd",
        role="RESIDENT",
        email="test@example.com",
        id="123"
    )

    mock_dynamodb.execute_transaction.assert_called_once()

    args, kwargs = mock_dynamodb.execute_transaction.call_args
    transact_items = kwargs["TransactStatements"]

    assert len(transact_items) == 2
    assert transact_items[0]["Parameters"][0]["S"] == "hashed_pwd"
    assert transact_items[1]["Parameters"][1]["S"] == "USERS"

@pytest.mark.asyncio
async def test_change_password_dynamodb_exception(mocker):
    # Arrange
    mock_dynamodb = MagicMock()
    mock_dynamodb.execute_transaction.side_effect = Exception("DDB failure")

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=MagicMock
    )

    # Act + Assert
    with pytest.raises(AppException) as exc:
        await repo.change_password(
            new_password="hashed_pwd",
            role="RESIDENT",
            email="test@example.com",
            id="123"
        )

    assert exc.value.error_code == USER_007
    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal Server Error"

@pytest.mark.asyncio
async def test_get_user_by_email_success():

    mock_dynamodb = MagicMock()
    mock_deserializer = MagicMock()

    mock_deserializer.deserialize.side_effect = lambda x: x["S"]

    mock_dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "id": {"S": "123"},
                "first_name": {"S": "Test"},
                "middle_name": {"S": ""},
                "last_name": {"S": "User"},
                "email": {"S": "test@example.com"},
                "password": {"S": "hashed"},
                "flat": {"S": "101"},
                "mobile_number": {"S": "9999999999"},
                "role": {"S": UserRole.ROLERESIDENT},
            }
        ]
    }

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=lambda: mock_deserializer,
    )


    user = await repo.get_user_by_email("test@example.com")


    assert isinstance(user, User)
    assert user.email == "test@example.com"
    assert user.first_name == "Test"

    mock_dynamodb.execute_statement.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_by_email_db_exception():

    mock_dynamodb = MagicMock()
    mock_dynamodb.execute_statement.side_effect = Exception("DB error")

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )


    with pytest.raises(AppException) as exc:
        await repo.get_user_by_email("test@example.com")

    assert exc.value.error_code == USER_005
    assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_get_user_by_email_user_not_found():

    mock_dynamodb = MagicMock()
    mock_dynamodb.execute_statement.return_value = {"Items": []}

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    with pytest.raises(AppException) as exc:
        await repo.get_user_by_email("missing@example.com")

    assert exc.value.error_code == USER_003
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_add_user_success():

    mock_dynamodb = MagicMock()

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    user = User(
        id="123",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9999999999",
        email="test@example.com",
        flat="101",
        password="hashed_password",
        role=UserRole.ROLERESIDENT,
    )

    await repo.add_user(user)

    mock_dynamodb.execute_transaction.assert_called_once()

    args, kwargs = mock_dynamodb.execute_transaction.call_args

    transact_statements = kwargs["TransactStatements"]
    assert len(transact_statements) == 2

    assert transact_statements[0]["Parameters"][0]["S"] == "USERS"
    assert transact_statements[0]["Parameters"][2]["S"] == user.email

    assert transact_statements[1]["Parameters"][0]["S"] == f"ROLE#{user.role.value}"
    assert transact_statements[1]["Parameters"][1]["S"] == user.id


@pytest.mark.asyncio
async def test_add_user_db_exception():

    mock_dynamodb = MagicMock()
    mock_dynamodb.execute_transaction.side_effect = Exception("DynamoDB error")

    repo = UserRepository(
        ddb_connection=mock_dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    user = User(
        id="123",
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9999999999",
        email="test@example.com",
        flat="101",
        password="hashed_password",
        role=UserRole.ROLERESIDENT,
    )

    with pytest.raises(AppException) as exc:
        await repo.add_user(user)

    assert exc.value.error_code == USER_008
    assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_get_user_by_id_and_role_success():

    user_id = uuid.uuid4()

    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {
        "Items": [
            {
                "id": {"S": str(user_id)},
                "email": {"S": "test@example.com"},
                "first_name": {"S": "Test"},
                "middle_name": {"S": ""},
                "last_name": {"S": "User"},
                "mobile_number": {"S": "9999999999"},
                "flat": {"S": "101"},
                "password": {"S": "hashed"},
                "role": {"S": UserRole.ROLERESIDENT.value},
            }
        ]
    }

    deserializer = MagicMock()
    deserializer.deserialize.side_effect = lambda x: list(x.values())[0]

    repo = UserRepository(
        ddb_connection=dynamodb,
        table_name="UserTable",
        deserializer=lambda: deserializer,
    )

    user = await repo.get_user_by_id_and_role(UserRole.ROLERESIDENT, user_id)

    assert isinstance(user, User)
    assert user.id == str(user_id)
    assert user.email == "test@example.com"
    assert user.role == UserRole.ROLERESIDENT

    dynamodb.execute_statement.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_by_id_and_role_user_not_found():

    dynamodb = MagicMock()
    dynamodb.execute_statement.return_value = {"Items": []}

    repo = UserRepository(
        ddb_connection=dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    with pytest.raises(AppException) as exc:
        await repo.get_user_by_id_and_role(UserRole.ROLEADMIN, uuid.uuid4())

    assert exc.value.error_code == USER_006
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_user_by_id_and_role_db_exception():

    dynamodb = MagicMock()
    dynamodb.execute_statement.side_effect = Exception("DynamoDB failure")

    repo = UserRepository(
        ddb_connection=dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    with pytest.raises(AppException) as exc:
        await repo.get_user_by_id_and_role(UserRole.ROLEOFFICER, uuid.uuid4())

    assert exc.value.error_code == USER_009
    assert exc.value.status_code == 500

@pytest.fixture
def user():
    return User(
        id=str(uuid.uuid4()),
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9999999999",
        email="new@example.com",
        flat="101",
        password="hashed",
        role=UserRole.ROLERESIDENT,
    )

@pytest.mark.asyncio
async def test_update_profile_with_email_change(user):
    dynamodb = MagicMock()

    repo = UserRepository(
        ddb_connection=dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    old_email = "old@example.com"

    await repo.update_profile(user, old_email)

    dynamodb.execute_transaction.assert_called_once()

    kwargs = dynamodb.execute_transaction.call_args.kwargs
    statements = kwargs["TransactStatements"]

    assert len(statements) == 3

    assert statements[0]["Statement"].startswith("UPDATE")

    assert statements[1]["Statement"].startswith("DELETE")

    assert statements[2]["Statement"].startswith("INSERT")

@pytest.mark.asyncio
async def test_update_profile_without_email_change(user):
    dynamodb = MagicMock()

    repo = UserRepository(
        ddb_connection=dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    await repo.update_profile(user, old_email=user.email)

    dynamodb.execute_transaction.assert_called_once()

    kwargs = dynamodb.execute_transaction.call_args.kwargs
    statements = kwargs["TransactStatements"]

    assert len(statements) == 2

    assert statements[0]["Statement"].startswith("UPDATE")

    assert statements[1]["Statement"].startswith("UPDATE")

@pytest.mark.asyncio
async def test_update_profile_db_exception(user):
    dynamodb = MagicMock()
    dynamodb.execute_transaction.side_effect = Exception("DynamoDB down")

    repo = UserRepository(
        ddb_connection=dynamodb,
        table_name="UserTable",
        deserializer=MagicMock,
    )

    with pytest.raises(AppException) as exc:
        await repo.update_profile(user, old_email="old@example.com")

    assert exc.value.error_code == USER_010
    assert exc.value.status_code == 500
