from fastapi import HTTPException, status

def test_login_success(client, mocker):
    mock_response = {
        "token": "fake-jwt",
        "email": "test@example.com",
        "role": "USER",
    }

    mocker.patch(
        "internal.handler.auth_handler.user_service_instance.get_user_by_email_and_password",
        return_value=mock_response,
    )

    response = client.post("/login", json={"email": "test@example.com", "password": "password"},)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Login Successful"
    assert body["data"]["email"] == "test@example.com"
    assert body["data"]["role"] == "USER"
    assert body["data"]["token"] == "fake-jwt"


def test_login_invalid_credentials(client, mocker):
    mocker.patch(
        "internal.handler.auth_handler.user_service_instance.get_user_by_email_and_password",
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        ),
    )

    response = client.post(
        "/login",
        json={"email": "wrong@example.com", "password": "wrong"},
    )

    assert response.status_code == 401

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Invalid Credentials"
    assert body["errorcode"] == 1001


def test_login_internal_server_error(client, mocker):
    mocker.patch(
        "internal.handler.auth_handler.user_service_instance.get_user_by_email_and_password",
        side_effect=Exception("DB down"),
    )

    response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 500

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"
    assert body["errorcode"] == 1010

def test_login_invalid_email_format(client):
    response = client.post(
        "/login",
        json={
            "email": "not-an-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_signup_success(client, mocker):
    mock_add_user = mocker.patch(
        "internal.handler.auth_handler.user_service_instance.add_user",
        return_value=None,
    )

    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "A",
            "lastName": "Doe",
            "mobile": "9876543210",
            "email": "john.doe@example.com",
            "flat": "101",
            "password": "Strong@Password1",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Sign in Successful"
    assert body["data"] is None

    mock_add_user.assert_called_once()

from fastapi import HTTPException, status

def test_signup_email_already_exists(client, mocker):
    mocker.patch(
        "internal.handler.auth_handler.user_service_instance.add_user",
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already exists",
        ),
    )

    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "A",
            "lastName": "Doe",
            "mobile": "9876543210",
            "email": "john.doe@example.com",
            "flat": "101",
            "password": "Strong@Password1",
        },
    )

    assert response.status_code == 401

    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "User already exists"
    assert body["errorcode"] == 1001

def test_signup_invalid_email(client):
    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "",
            "lastName": "Doe",
            "mobile": "9876543210",
            "email": "invalid-email",
            "flat": "101",
            "password": "Strong@Password1",
        },
    )

    assert response.status_code == 422

def test_signup_weak_password(client):
    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "",
            "lastName": "Doe",
            "mobile": "9876543210",
            "email": "john@example.com",
            "flat": "101",
            "password": "weakpassword",
        },
    )

    assert response.status_code == 422

def test_signup_missing_last_name(client):
    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "",
            "mobile": "9876543210",
            "email": "john@example.com",
            "flat": "101",
            "password": "Strong@Password1",
        },
    )

    assert response.status_code == 422

def test_signup_invalid_flat(client):
    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "",
            "lastName": "Doe",
            "mobile": "9876543210",
            "email": "john@example.com",
            "flat": "999",
            "password": "Strong@Password1",
        },
    )

    assert response.status_code == 422

def test_signup_extra_field(client):
    response = client.post(
        "/signup",
        json={
            "firstName": "John",
            "middleName": "",
            "lastName": "Doe",
            "mobile": "9876543210",
            "email": "john@example.com",
            "flat": "101",
            "password": "Strong@Password1",
            "role": "admin",
        },
    )

    assert response.status_code == 422

