from internal.repository.user_repository import (
    UserRepository,
)
from boto3.dynamodb.types import TypeDeserializer
from internal.dependencies.dependencies import db_connection
from internal.constants.constants import TABLENAME

user_repository_instance = UserRepository(db_connection, TABLENAME, TypeDeserializer)
