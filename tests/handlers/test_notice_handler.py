from internal.models.user import UserRole
from http import HTTPStatus
from fastapi import HTTPException, status


def test_issue_notice_admin_success(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.issue_notice",
        return_value=None,
    )

    response = client.post(
        "/notices/issue",
        json={"content": "Maintenance tomorrow"},
    )

    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Notice issued successfully"
    assert body["data"] is None


def test_issue_notice_officer_success(client , mocker, override_jwt):
    override_jwt(role=UserRole.ROLEOFFICER)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.issue_notice",
        return_value=None,
    )

    response = client.post(
        "/notices/issue",
        json={"content": "Water supply shutdown"},
    )

    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert body["status"] == "Success"
    assert body["message"] == "Notice issued successfully"
    assert body["data"] is None


def test_issue_notice_unauthorized_role(client, override_jwt):
    override_jwt(role=UserRole.ROLERESIDENT)

    response = client.post(
        "/notices/issue",
        json={"content": "Should not work"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Unauthorized access"



def test_issue_notice_http_exception(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.issue_notice",
        side_effect=HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid notice content",
        ),
    )

    response = client.post(
        "/notices/issue",
        json={"content": ""},
    )

    assert response.status_code == 422

def test_issue_notice_http_exception(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.issue_notice",
        side_effect=HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request"),
    )

    response = client.post(
        "/notices/issue",
        json={"content": "Notice"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Bad request"


def test_issue_notice_internal_error(client, mocker, override_jwt):
    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.issue_notice",
        side_effect=Exception("DB down"),
    )

    response = client.post(
        "/notices/issue",
        json={"content": "Notice"},
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_all_notices_success(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    fake_notices = [
        {"id": "1", "content": "Notice 1"},
        {"id": "2", "content": "Notice 2"},
    ]

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices",
        return_value=fake_notices,
    )

    response = client.get("/notices")

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Notices fetched successfully"
    assert body["data"] == fake_notices


def test_get_all_notices_http_exception(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices",
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No notices found",
        ),
    )

    response = client.get("/notices")

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "No notices found"


def test_get_all_notices_internal_error(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices",
        side_effect=Exception("DB down"),
    )


    response = client.get("/notices")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_notices_by_year_success(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    fake_notices = [
        {"id": "1", "content": "Notice Jan"},
        {"id": "2", "content": "Notice Feb"},
    ]

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices_by_month_and_year",
        return_value=fake_notices,
    )

    response = client.get("/notices/month-year?year=2025")

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Notices fetched successfully"
    assert body["data"] == fake_notices


def test_get_notices_by_year_and_month_success(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    fake_notices = [
        {"id": "1", "content": "March Notice"},
    ]

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices_by_month_and_year",
        return_value=fake_notices,
    )

    response = client.get("/notices/month-year?year=2025&month=3")

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Notices fetched successfully"
    assert body["data"] == fake_notices


def test_get_notices_by_month_year_http_exception(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices_by_month_and_year",
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No notices found",
        ),
    )

    response = client.get("/notices/month-year?year=2025&month=4")

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "No notices found"


def test_get_notices_by_month_year_internal_error(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.notice_handler.notice_service_instance.get_all_notices_by_month_and_year",
        side_effect=Exception("DB down"),
    )


    response = client.get("/notices/month-year?year=2025&month=5")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_notices_invalid_year(client, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    response = client.get("/notices/month-year?year=0")

    assert response.status_code == 422


def test_get_notices_invalid_month(client, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    response = client.get("/notices/month-year?year=2025&month=13")

    assert response.status_code == 422
