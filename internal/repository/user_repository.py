from internal.models.user import User, UserRole
from internal.errors.base_exception import AppException
from internal.constants.constants import *
import asyncio
import uuid


class UserRepository:

    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name


    async def change_password(self, new_password: str, role: str, email: str, id: str):
        update_statement = (
            f"UPDATE {self.table_name} SET password = ? WHERE PK = ? AND SK = ?"
        )

        try:
            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements=[
                    {
                        "Statement": update_statement,
                        "Parameters": [
                            {"S": new_password},
                            {"S": f"ROLE#{role}"},
                            {"S": id},
                        ],
                    },
                    {
                        "Statement": update_statement,
                        "Parameters": [
                            {"S": new_password},
                            {"S": "USERS"},
                            {"S": f"{email}#{id}"},
                        ],
                    },
                ],
            )
        except Exception:
            raise AppException(USER_007)

    async def get_user_by_email(self, email: str):
        statement = (
            f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)"
        )

        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=statement,
                Parameters=[{"S": "USERS"}, {"S": email}],
            )
        except Exception:
            raise AppException(USER_005)

        items = response["Items"]

        if len(items) == 0:
            raise AppException(USER_003)

        for item in items:
            user_details = {
                k: self.deserializer.deserialize(v) for k, v in item.items()
            }

        user: User = User.model_construct(**user_details)

        return user

    async def add_user(self, new_user: User):
        statement = f"INSERT INTO {self.table_name} VALUE {{'PK': ?, 'SK': ?, 'email': ?, 'first_name': ?, 'flat': ?, 'id': ?, 'middle_name': ?, 'last_name': ?, 'mobile_number': ?, 'password': ?, 'role': ?}}"

        try:
            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements=[
                    {
                        "Statement": statement,
                        "Parameters": [
                            {"S": "USERS"},
                            {"S": (new_user.email + "#" + new_user.id)},
                            {"S": new_user.email},
                            {"S": new_user.first_name},
                            {"S": new_user.flat},
                            {"S": new_user.id},
                            {"S": new_user.middle_name},
                            {"S": new_user.last_name},
                            {"S": new_user.mobile_number},
                            {"S": new_user.password},
                            {"S": new_user.role.value},
                        ],
                    },
                    {
                        "Statement": statement,
                        "Parameters": [
                            {"S": ("ROLE" + "#" + new_user.role.value)},
                            {"S": new_user.id},
                            {"S": new_user.email},
                            {"S": new_user.first_name},
                            {"S": new_user.flat},
                            {"S": new_user.id},
                            {"S": new_user.middle_name},
                            {"S": new_user.last_name},
                            {"S": new_user.mobile_number},
                            {"S": new_user.password},
                            {"S": new_user.role.value},
                        ],
                    },
                ],
            )
        except Exception:
            raise AppException(USER_008)

    async def get_user_by_id_and_role(self, role: UserRole, id: uuid.UUID):
        statement = (
            f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)"
        )

        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=statement,
                Parameters=[{"S": f"ROLE#{role.value}"}, {"S": str(id)}],
            )
        except Exception:
            raise AppException(USER_009)

        items = response["Items"]

        if len(items) == 0:
            raise AppException(USER_006)

        for item in items:
            user_details = {
                k: self.deserializer.deserialize(v) for k, v in item.items()
            }

        user: User = User.model_construct(**user_details)

        return user

    async def update_profile(self, user: User, old_email: str | None = None):

        transact_statements = []

        transact_statements.append({
            "Statement": f'UPDATE "{self.table_name}" SET first_name=?, middle_name=?, last_name=?, mobile_number=?, email=? WHERE PK=? AND SK=?',
            "Parameters": [
                {"S": user.first_name}, {"S": user.middle_name or ""}, {"S": user.last_name},
                {"S": user.mobile_number}, {"S": user.email},
                {"S": f"ROLE#{user.role}"}, {"S": str(user.id)}
            ]
        })

        if old_email and old_email != user.email:
            transact_statements.extend([
                {
                    "Statement": f'DELETE FROM "{self.table_name}" WHERE PK=? AND SK=?',
                    "Parameters": [{"S": "USERS"}, {"S": f"{old_email}#{user.id}"}]
                },
                {
                    "Statement": f"INSERT INTO {self.table_name} VALUE {{'PK': ?, 'SK': ?, 'email': ?, 'first_name': ?, 'flat': ?, 'id': ?, 'middle_name': ?, 'last_name': ?, 'mobile_number': ?, 'password': ?, 'role': ?}}",
                    "Parameters": [
                        {"S": "USERS"}, {"S": f"{user.email}#{user.id}"}, {"S": user.email},
                        {"S": user.first_name}, {"S": user.flat}, {"S": str(user.id)},
                        {"S": user.middle_name or ""}, {"S": user.last_name},
                        {"S": user.mobile_number}, {"S": user.password}, {"S": str(user.role)}
                    ]
                }
            ])
        else:
            transact_statements.append({
                "Statement": f'UPDATE "{self.table_name}" SET first_name=?, middle_name=?, last_name=?, mobile_number=? WHERE PK=? AND SK=?',
                "Parameters": [
                    {"S": user.first_name}, {"S": user.middle_name or ""}, 
                    {"S": user.last_name}, {"S": user.mobile_number},
                    {"S": "USERS"}, {"S": f"{user.email}#{user.id}"}
                ]
            })

        try:
            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements= transact_statements
            )
        except Exception:
            raise AppException(USER_010)
