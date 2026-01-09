from fastapi import HTTPException, status
from typing import List
from internal.models.user import User, UserRole
from internal.errors.base_exception import AppException
from internal.constants.constants import *
import asyncio
from uuid import UUID

class SocietyRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    async def get_all_users_by_role(self, role: UserRole):
        try:
            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                Parameters=[{"S": ("ROLE#" + role)}]
            )
        except:
            raise AppException(SOCIETY_003)

        items = response["Items"]

        users: List[User] = []

        for item in items:
            user_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}
            
            user: User = User.model_construct(**user_details)

            users.append(user) 

        return users  
    
    async def delete_user(self, id: UUID, role: UserRole):
        try:
            role_str = str(role.value)
            user_id_str = str(id)

            response = await asyncio.to_thread(
                self.dynamodb.execute_statement,
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ? AND SK = ?",
                Parameters=[
                    {"S": f"ROLE#{role_str}"},
                    {"S": user_id_str}
                ]
            )
            
            items = response.get("Items", [])
            if not items:
                raise AppException(SOCIETY_001)
            
            user_data = {k: self.deserializer.deserialize(v) for k, v in items[0].items()}
            email = user_data.get("email")
            
            if not email:
                raise AppException(SOCIETY_002)

            await asyncio.to_thread(
                self.dynamodb.execute_transaction,
                TransactStatements=[
                    {
                        "Statement": f"DELETE FROM {self.table_name} WHERE PK = ? AND SK = ?",
                        "Parameters": [
                            {"S": f"ROLE#{role_str}"},
                            {"S": user_id_str}
                        ]
                    },
                    {
                        "Statement": f"DELETE FROM {self.table_name} WHERE PK = ? AND SK = ?",
                        "Parameters": [
                            {"S": "USERS"},
                            {"S": f"{email}#{user_id_str}"}
                        ]
                    }
                ]
            )
        except:
            raise AppException(SOCIETY_004)