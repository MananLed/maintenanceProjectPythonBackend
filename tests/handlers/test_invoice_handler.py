from internal.models.user import UserRole
from http import HTTPStatus
from fastapi import HTTPException

VALID_INVOICE_PAYLOAD = {
    "amount": 1500.50
}

MOCK_INVOICES = [
    {"id": "1", "amount": 1200, "month": 9, "year": 2025},
    {"id": "2", "amount": 1500, "month": 9, "year": 2025},
]


# def test_issue_invoice_success_admin(client, mocker, override_jwt):
#     override_jwt(role=UserRole.ROLEADMIN)

#     mocker.patch(
#         "internal.handler.invoice_handler.invoice_service_instance.issue_invoice",
#         return_value=None,
#     )

#     response = client.post(
#         "/invoices/issue",
#         json=VALID_INVOICE_PAYLOAD,
#     )

#     assert response.status_code == HTTPStatus.CREATED
#     body = response.json()

#     assert body["status"] == "Success"
#     assert body["message"] == "Invoice issued successfully"
#     assert body["data"] is None


# def test_issue_invoice_success_officer(client, mocker, override_jwt):
#     override_jwt(role=UserRole.ROLEOFFICER)

#     mocker.patch(
#         "internal.handler.invoice_handler.invoice_service_instance.issue_invoice",
#         return_value=None,
#     )

#     response = client.post(
#         "/invoices/issue",
#         json=VALID_INVOICE_PAYLOAD,
#     )
#     body = response.json()

#     assert response.status_code == HTTPStatus.CREATED
#     assert body["status"] == "Success"
#     assert body["message"] == "Invoice issued successfully"
#     assert body["data"] is None


# def test_issue_invoice_unauthorized(client,  override_jwt):
#     override_jwt(role=UserRole.ROLERESIDENT)

#     response = client.post(
#         "/invoices/issue",
#         json=VALID_INVOICE_PAYLOAD,
#     )

#     assert response.status_code == HTTPStatus.UNAUTHORIZED
#     body = response.json()

#     assert body["status"] == "fail"
#     assert body["message"] == "Unauthorized access"


# def test_issue_invoice_http_exception(client, mocker, override_jwt):
#     override_jwt(role=UserRole.ROLEADMIN)

#     mocker.patch(
#         "internal.handler.invoice_handler.invoice_service_instance.issue_invoice",
#         side_effect=HTTPException(
#             status_code=HTTPStatus.BAD_REQUEST,
#             detail="Invalid invoice",
#         ),
#     )


#     response = client.post(
#         "/invoices/issue",
#         json=VALID_INVOICE_PAYLOAD,
#     )

#     assert response.status_code == HTTPStatus.BAD_REQUEST
#     body = response.json()

#     assert body["status"] == "fail"
#     assert body["message"] == "Invalid invoice"


# def test_issue_invoice_internal_error(client, mocker, override_jwt):
#     override_jwt(role=UserRole.ROLEADMIN)

#     mocker.patch(
#         "internal.handler.invoice_handler.invoice_service_instance.issue_invoice",
#         side_effect=Exception("DB down"),
#     )

#     response = client.post(
#         "/invoices/issue",
#         json=VALID_INVOICE_PAYLOAD,
#     )

#     assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
#     body = response.json()

#     assert body["status"] == "fail"
#     assert body["message"] == "Internal Server Error"


# def test_issue_invoice_invalid_amount(client, override_jwt):
#     override_jwt(role=UserRole.ROLEADMIN)

#     response = client.post(
#         "/invoices/issue",
#         json={"amount": -100},
#     )

#     assert response.status_code == 422


def test_get_invoices_by_month_year_success(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.invoice_handler.invoice_service_instance.get_all_invoices_by_month_and_year",
        return_value=MOCK_INVOICES,
    )

    response = client.get(
        "/invoices/month-year?year=2025&month=9"
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Invoices fetched successfully"
    assert body["data"] == MOCK_INVOICES


def test_get_invoices_by_year_only(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.invoice_handler.invoice_service_instance.get_all_invoices_by_month_and_year",
        return_value=MOCK_INVOICES,
    )

    response = client.get(
        "/invoices/month-year?year=2025"
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()

    assert body["status"] == "Success"
    assert body["message"] == "Invoices fetched successfully"
    assert body["data"] == MOCK_INVOICES


def test_get_invoices_http_exception(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.invoice_handler.invoice_service_instance.get_all_invoices_by_month_and_year",
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No invoices found",
        ),
    )

    response = client.get(
        "/invoices/month-year?year=2025&month=9"
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "No invoices found"



def test_get_invoices_internal_error(client, mocker, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    mocker.patch(
        "internal.handler.invoice_handler.invoice_service_instance.get_all_invoices_by_month_and_year",
        side_effect=Exception("DB down"),
    )

    response = client.get(
        "/invoices/month-year?year=2025&month=9"
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.json()

    assert body["status"] == "fail"
    assert body["message"] == "Internal Server Error"


def test_get_invoices_invalid_year(client, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    response = client.get(
        "/invoices/month-year?year=-2025"
    )

    assert response.status_code == 422

def test_get_invoices_invalid_month(client, override_jwt):

    override_jwt(role=UserRole.ROLEADMIN)

    response = client.get("/invoices/month-year?year=2025&month=13")

    assert response.status_code == 422