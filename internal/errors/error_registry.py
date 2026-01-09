from dataclasses import dataclass 
from fastapi import status
from typing import Dict

@dataclass(frozen=True)
class ErrorDefinition:
    http_status: int
    message: str 

db_exception: ErrorDefinition = ErrorDefinition(
    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    message="Internal Server Error"
)

sys_exception: ErrorDefinition = ErrorDefinition(
    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    message="Internal Server Error"
)

unauthorized_exception: ErrorDefinition = ErrorDefinition(
    http_status=status.HTTP_401_UNAUTHORIZED,
    message="Unauthorized access"
)


ERROR_REGISTRY: Dict[str, ErrorDefinition] = {
    "FEEDBACK_001": ErrorDefinition(
        http_status=status.HTTP_401_UNAUTHORIZED,
        message = "Unauthorized to perform the action"
    ),
    "FEEDBACK_002": ErrorDefinition(
        http_status=status.HTTP_400_BAD_REQUEST,
        message="Feedback can only be given on completed request"
    ),
    "FEEDBACK_003": ErrorDefinition(
        http_status=status.HTTP_409_CONFLICT,
        message="Feedback is already given"
    ),
    "FEEDBACK_004": db_exception,
    "FEEDBACK_005": db_exception,
    "FEEDBACK_006": db_exception,
    "SOCIETY_001": ErrorDefinition(
        http_status=status.HTTP_404_NOT_FOUND,
        message="User not found"
    ),
    "SOCIETY_002": ErrorDefinition(
        http_status=status.HTTP_417_EXPECTATION_FAILED,
        message="User record is missing Email field"
    ),
    "SOCIETY_003": db_exception,
    "SOCIETY_004": db_exception,
    "NOTICE_001": db_exception,
    "NOTICE_002": db_exception,
    "NOTICE_003": db_exception,
    "INVOICE_001": db_exception,
    "INVOICE_002": db_exception,
    "REQUEST_001": unauthorized_exception,
    "REQUEST_002": ErrorDefinition(
        http_status=status.HTTP_400_BAD_REQUEST,
        message="Invalid request: Slot ID out of range"
    ),
    "REQUEST_003": ErrorDefinition(
        http_status=status.HTTP_409_CONFLICT,
        message="Only pending request can be approved"
    ),
    "REQUEST_004": ErrorDefinition(
        http_status=status.HTTP_409_CONFLICT,
        message="Only approved request can be marked completed"
    ),
    "REQUEST_005": ErrorDefinition(
        http_status=status.HTTP_409_CONFLICT,
        message="Request is either approved or completed already"
    ),
    "REQUEST_006": ErrorDefinition(
        http_status=status.HTTP_400_BAD_REQUEST,
        message="User already has a request with the service type for today"
    ),
    "REQUEST_007": ErrorDefinition(
        http_status=status.HTTP_404_NOT_FOUND,
        message="Request with given id not found."
    ),
    "REQUEST_008": ErrorDefinition(
        http_status=status.HTTP_409_CONFLICT,
        message="Only pending request can be cancelled"
    ),
    "REQUEST_009": unauthorized_exception,
    "REQUEST_010": ErrorDefinition(
        http_status=status.HTTP_400_BAD_REQUEST,
        message="Invalid request: Slot ID out of range"
    ),
    "REQUEST_011": db_exception,
    "REQUEST_012": db_exception,
    "REQUEST_013": db_exception,
    "REQUEST_014": db_exception,
    "REQUEST_015": db_exception,
    "REQUEST_016": db_exception,
    "USER_001": ErrorDefinition(
        http_status=status.HTTP_401_UNAUTHORIZED,
        message="Old password does'nt match"
    ),
    "USER_002": ErrorDefinition(
        http_status=status.HTTP_400_BAD_REQUEST,
        message="No change in the password"
    ),
    "USER_003": ErrorDefinition(
        http_status=status.HTTP_401_UNAUTHORIZED,
        message="Invalid Credentials"
    ),
    "USER_004": ErrorDefinition(
        http_status=status.HTTP_409_CONFLICT,
        message="User with given email already exists"
    ),
    "USER_005": db_exception,
    "USER_006": ErrorDefinition(
        http_status=status.HTTP_404_NOT_FOUND,
        message="User not found"
    ),
    "USER_007": db_exception,
    "USER_008": db_exception,
    "USER_009": db_exception,
    "USER_010": db_exception,
    "AUTH_001": ErrorDefinition(
        http_status=status.HTTP_401_UNAUTHORIZED,
        message="Authorization header missing or invalid"
    ),
    "AUTH_002": ErrorDefinition(
        http_status=status.HTTP_401_UNAUTHORIZED,
        message="Invalid or expired token"
    ),
    "AUTH_003": ErrorDefinition(
        http_status=status.HTTP_401_UNAUTHORIZED,
        message="Authentication context missing"
    ),
    "AUTH_004": unauthorized_exception,
    "SYS_001": sys_exception
}