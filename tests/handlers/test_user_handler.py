from internal.models.user import User, UserRole
from fastapi import HTTPException, status
import uuid

def test_get_profile_success(client, mocker, override_jwt):

    override_jwt(role="resident")

    fake_user = User(
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="DummyPassword@123", 
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        return_value=fake_user,
    )

    response = client.get("/profile")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Profile fetched successfully"

    data = body["data"]
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert data["role"] == "resident"

def test_get_profile_service_http_exception(client, mocker, override_jwt):

    override_jwt(role="resident")
    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        side_effect=HTTPException(
            status_code=404,
            detail="User not found",
        ),
    )

    response = client.get("/profile")

    assert response.status_code == 404

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "User not found"

def test_get_profile_internal_error(client, mocker, override_jwt):
    override_jwt(role="resident")
    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        side_effect=Exception("DB down"),
    )

    response = client.get("/profile")

    assert response.status_code == 500

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"

def test_get_profile_missing_token(client):
    response = client.get("/profile")

    assert response.status_code == 401

    body = response.json()
    assert body["detail"] == "Authorization header missing or invalid"

def test_get_profile_invalid_token(client):
    response = client.get(
        "/profile",
        headers={"Authorization": "Bearer invalid.token"},
    )

    assert response.status_code == 401

from internal.models.user import User, UserRole


def test_change_password_success(client, mocker, override_jwt):
    override_jwt(role="resident")
    fake_user = User(
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="OldPassword@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        return_value=fake_user,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.change_password",
        return_value=None,
    )

    response = client.patch(
        "/profile/password",
        json={
            "oldPassword": "OldPassword@123",
            "newPassword": "NewStrongPassword@123!",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Password changed successfully"
    assert body["data"] is None

def test_change_password_invalid_new_password(client, override_jwt):
    override_jwt(role="resident")
    response = client.patch(
        "/profile/password",
        json={
            "oldPassword": "OldPassword@123",
            "newPassword": "weakpassword",
        },
    )

    assert response.status_code == 422

def test_change_password_user_not_found(client, mocker, override_jwt):
    override_jwt(role="resident")
    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    response = client.patch(
        "/profile/password",
        json={
            "oldPassword": "OldPassword@123",
            "newPassword": "NewStrongPassword@123!",
        },
    )

    assert response.status_code == 404

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "User not found"


def test_change_password_wrong_old_password(client, mocker, override_jwt):
    override_jwt(role="resident")
    fake_user = User(
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="CorrectOld@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        return_value=fake_user,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.change_password",
        side_effect=HTTPException(
            status_code=400,
            detail="Old password is incorrect",
        ),
    )

    response = client.patch(
        "/profile/password",
        json={
            "oldPassword": "WrongPassword@123",
            "newPassword": "NewStrongPassword@123!",
        },
    )

    assert response.status_code == 400

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Old password is incorrect"


def test_change_password_internal_error(client, mocker, override_jwt):
    override_jwt(role="resident")
    fake_user = User(
        first_name="Test",
        middle_name="",
        last_name="User",
        mobile_number="9876543210",
        email="test@example.com",
        flat="101",
        password="OldPassword@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_email",
        return_value=fake_user,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.change_password",
        side_effect=Exception("DB down"),
    )

    response = client.patch(
        "/profile/password",
        json={
            "oldPassword": "OldPassword@123",
            "newPassword": "NewStrongPassword@123!",
        },
    )

    assert response.status_code == 500

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


#delete profile to be tested


def test_update_profile_success(client, mocker, override_jwt):

    override_jwt(role="resident")


    fake_user = User(
        first_name="OldFirst",
        middle_name="OldMiddle",
        last_name="OldLast",
        mobile_number="9876543210",
        email="old@example.com",
        flat="101",
        password="DummyPassword@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_id_and_role",
        return_value=fake_user,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.update_profile",
        return_value=None,
    )

    response = client.patch(
        "/profile/update",
        json={
            "firstname": "NewFirst",
            "middlename": "NewMiddle",
            "lastname": "NewLast",
            "mobile": "9876543211",
            "email": "new@example.com",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Profile updated successfully"
    assert body["data"] is None

    assert fake_user.first_name == "NewFirst"
    assert fake_user.middle_name == "NewMiddle"
    assert fake_user.last_name == "NewLast"
    assert fake_user.mobile_number == "9876543211"
    assert fake_user.email == "new@example.com"


def test_update_profile_internal_error(client, mocker, override_jwt):

    override_jwt(role="resident")

    fake_user = User(
        first_name="OldFirst",
        middle_name="OldMiddle",
        last_name="OldLast",
        mobile_number="9876543210",
        email="old@example.com",
        flat="101",
        password="DummyPassword@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_id_and_role",
        return_value=fake_user,
    )
    mocker.patch(
        "internal.handler.user_handler.user_service_instance.update_profile",
        side_effect=Exception("DB down"),
    )

    response = client.patch(
        "/profile/update",
        json={
            "firstname": "NewFirst",
            "middlename": "NewMiddle",
            "lastname": "NewLast",
            "mobile": "9876543211",
            "email": "new@example.com",
        },
    )

    assert response.status_code == 500
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"

def test_update_profile_partial_update(client, mocker, override_jwt):

    override_jwt(role="resident")

    fake_user = User(
        first_name="OldFirst",
        middle_name="OldMiddle",
        last_name="OldLast",
        mobile_number="9876543210",
        email="old@example.com",
        flat="101",
        password="DummyPassword@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_id_and_role",
        return_value=fake_user,
    )
    mocker.patch(
        "internal.handler.user_handler.user_service_instance.update_profile",
        return_value=None,
    )

    response = client.patch(
        "/profile/update",
        json={
            "firstname": "NewFirst",
            "middlename": "",
            "lastname": "",
            "mobile": "",
            "email": "",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Profile updated successfully"

    assert fake_user.first_name == "NewFirst"
    assert fake_user.middle_name == "OldMiddle"
    assert fake_user.last_name == "OldLast"
    assert fake_user.mobile_number == "9876543210"
    assert fake_user.email == "old@example.com"

def test_update_profile_user_not_found(client, mocker, override_jwt):

    override_jwt(role="resident")

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_id_and_role",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ),
    )

    response = client.patch(
        "/profile/update",
        json={
            "firstname": "NewFirst",
            "middlename": "NewMiddle",
            "lastname": "NewLast",
            "mobile": "9876543211",
            "email": "new@example.com",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "User not found"

def test_update_profile_internal_error(client, mocker, override_jwt):

    override_jwt(role="resident")
    fake_user = User(
        first_name="OldFirst",
        middle_name="OldMiddle",
        last_name="OldLast",
        mobile_number="9876543210",
        email="old@example.com",
        flat="101",
        password="DummyPassword@123",
        role=UserRole.ROLERESIDENT,
    )

    mocker.patch(
        "internal.handler.user_handler.user_service_instance.get_user_by_id_and_role",
        return_value=fake_user,
    )
    mocker.patch(
        "internal.handler.user_handler.user_service_instance.update_profile",
        side_effect=Exception("DB down"),
    )

    response = client.patch(
        "/profile/update",
        json={
            "firstname": "NewFirst",
            "middlename": "NewMiddle",
            "lastname": "NewLast",
            "mobile": "9876543211",
            "email": "new@example.com",
        },
    )

    assert response.status_code == 500
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"
