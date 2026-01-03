from internal.repository.user_repository import (
    UserRepository
)
from internal.repository.society_repository import SocietyRepository
from internal.repository.feedback_repository import FeedbackRepository
from internal.repository.notice_repository import NoticeRepository
from internal.repository.invoice_repository import InvoiceRepository
from boto3.dynamodb.types import TypeDeserializer
from internal.dependencies.dependencies import db_connection
from internal.constants.constants import TABLENAME

user_repository_instance = UserRepository(db_connection, TABLENAME, TypeDeserializer)
society_repository_instance = SocietyRepository(db_connection, TABLENAME, TypeDeserializer)
feedback_repository_instance = FeedbackRepository(db_connection, TABLENAME, TypeDeserializer)
notice_repository_instance = NoticeRepository(db_connection, TABLENAME, TypeDeserializer)
invoice_repository_instance = InvoiceRepository(db_connection, TABLENAME, TypeDeserializer)