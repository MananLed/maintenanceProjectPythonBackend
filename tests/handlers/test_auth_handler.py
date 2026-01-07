from internal.service import user_service_instance

def test_login_success(client, mocker):
    mock_response = {
        "token": "fake-jwt",
        "email": "test@example.com",
        "role": "USER",
    }

    mocker.patch.object(
        user_service_instance,
        "get_user_by_email_and_password",
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