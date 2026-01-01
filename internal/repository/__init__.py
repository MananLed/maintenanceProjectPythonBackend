from internal.repository.user_repository import (
    UserRepository
)
from internal.repository.society_repository import SocietyRepository
from internal.repository.feedback_repository import FeedbackRepository
from boto3.dynamodb.types import TypeDeserializer
from internal.dependencies.dependencies import db_connection
from internal.constants.constants import TABLENAME

user_repository_instance = UserRepository(db_connection, TABLENAME, TypeDeserializer)
society_repository_instance = SocietyRepository(db_connection, TABLENAME, TypeDeserializer)
feedback_repository_instance = FeedbackRepository(db_connection, TABLENAME, TypeDeserializer)