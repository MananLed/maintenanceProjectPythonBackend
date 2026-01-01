from fastapi import HTTPException, status
from typing import List
from internal.models.user import User, UserRole


class SocietyRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    def get_all_users_by_role(self, role: UserRole):
        try:
            response = self.dynamodb.execute_statement(
                Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
                Parameters=[{"S": ("ROLE#" + role)}],
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        items = response["Items"]

        users: List[User] = []

        for item in items:
            user_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}

            user: User = User(user_details.get("first_name"), user_details.get("middle_name"), 
                          user_details.get("last_name"), user_details.get("mobile_number"), user_details.get("email"), 
                          user_details.get("flat"), user_details.get("password"), user_details.get("role"), user_details.get("id"))

            users.append(user) 

        return users  