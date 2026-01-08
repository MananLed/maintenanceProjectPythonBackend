from http import HTTPStatus
from uuid import uuid4
from internal.models.user import UserRole

def test_get_residents_success(client, mocker, override_jwt):
    override_jwt(role="admin")

    fake_residents = [
        {"first_name": "John", "email": "john@example.com"},
        {"first_name": "Alice", "email": "alice@example.com"},
    ]

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        return_value=fake_residents,
    )

    response = client.get("/society/residents")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Residents fetched successfully"
    assert body["data"] == fake_residents

def test_get_residents_unauthorized(client, mocker, override_jwt):
    override_jwt(role="resident")  

    response = client.get("/society/residents")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"

def test_get_residents_internal_error(client, mocker, override_jwt):
    override_jwt(role="admin")

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        side_effect=Exception("DB down"),
    )

    response = client.get("/society/residents")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"

def test_get_officers_success(client, mocker, override_jwt):
    override_jwt(role="admin")

    fake_officers = [
        {"first_name": "Officer1", "email": "officer1@example.com"},
        {"first_name": "Officer2", "email": "officer2@example.com"},
    ]

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        return_value=fake_officers,
    )

    response = client.get("/society/officers")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Officers fetched successfully"
    assert body["data"] == fake_officers


def test_get_officers_unauthorized(client, mocker, override_jwt):
    override_jwt(role="resident")  # non-admin

    response = client.get("/society/officers")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_get_officers_internal_error(client, mocker, override_jwt):
    override_jwt(role="admin")

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        side_effect=Exception("DB down"),
    )

    response = client.get("/society/officers")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"

#delete credentials of resident to be tested

def test_delete_officer_success(client, mocker, override_jwt):
    override_jwt(role="admin")
    officer_id = str(uuid4())

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.delete_user",
        return_value=None
    )

    response = client.delete(f"/credentials/officer?id={officer_id}")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Officer deleted successfully"
    assert body["data"] is None


def test_delete_officer_unauthorized(client, mocker, override_jwt):
    override_jwt(role="resident")  
    officer_id = str(uuid4())

    response = client.delete(f"/credentials/officer?id={officer_id}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_delete_officer_internal_error(client, mocker, override_jwt):
    override_jwt(role="admin")
    officer_id = str(uuid4())

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.delete_user",
        side_effect=Exception("DB down")
    )

    response = client.delete(f"/credentials/officer?id={officer_id}")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_add_officer_success(client, mocker, override_jwt):
    override_jwt(role="admin")
    officer_email = "officer@example.com"

    mocker.patch(
        "internal.handler.society_handler.user_service_instance.add_user",
        return_value=None
    )

    response = client.post(
        "/officers",
        json={"email": officer_email, "password": "Password@1234"}
    )

    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Officer created successfully"


def test_add_officer_unauthorized(client, override_jwt):
    override_jwt(role="resident")  
    officer_email = "officer@example.com"

    response = client.post(
        "/officers",
        json={"email": officer_email, "password": "Password@1234"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_add_officer_internal_error(client, mocker, override_jwt):
    override_jwt(role="admin")
    officer_email = "officer@example.com"

    mocker.patch(
        "internal.handler.society_handler.user_service_instance.add_user",
        side_effect=Exception("DB down")
    )

    response = client.post(
        "/officers",
        json={"email": officer_email, "password": "Password@1234"}
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_resident_count_success(client, mocker, override_jwt):
    override_jwt(role="admin")

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        return_value=[{"email": "res1"}, {"email": "res2"}]
    )

    response = client.get("/society/residents/count")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Residents count fetched successfully"
    assert body["data"] == 2


def test_get_resident_count_unauthorized(client, override_jwt):
    override_jwt(role="officer") 
    response = client.get("/society/residents/count")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_get_resident_count_internal_error(client, mocker, override_jwt):
    override_jwt(role="admin")

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        side_effect=Exception("DB down")
    )

    response = client.get("/society/residents/count")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_officer_count_success(client, mocker, override_jwt):
    override_jwt(role="admin")

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        return_value=[{"email": "off1"}, {"email": "off2"}, {"email": "off3"}]
    )

    response = client.get("/society/officers/count")
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Officers count fetched successfully"
    assert body["data"] == 3


def test_get_officer_count_unauthorized(client, override_jwt):
    override_jwt(role="resident") 
    response = client.get("/society/officers/count")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"


def test_get_officer_count_internal_error(client, mocker, override_jwt):
    override_jwt(role="admin")

    mocker.patch(
        "internal.handler.society_handler.society_service_instance.get_all_users_by_role",
        side_effect=Exception("DB down")
    )

    response = client.get("/society/officers/count")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"