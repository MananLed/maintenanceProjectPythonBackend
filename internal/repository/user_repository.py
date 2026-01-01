from internal.models.user import User
from fastapi import status, HTTPException

class UserRepository:
    def __init__(self, ddb_connection, table_name, deserializer):
        self.deserializer = deserializer()
        self.dynamodb = ddb_connection
        self.table_name = table_name

    def get_all_user_details(self):
        response = self.dynamodb.execute_statement(
            Statement=f"SELECT * FROM {self.table_name} WHERE PK = ?",
            Parameters=[{"S": "USERS"}],
        )

        items = response["Items"]

        for item in items:
            print({k: self.deserializer.deserialize(v) for k, v in item.items()})

        # get_all_user_details()

        # dynamodb.execute_transaction(
        #     TransactStatements = [
        #         {
        #             "Statement": """
        #                 UPDATE INVENTORY
        #                 SET stock = stock - ?
        #                 WHERE productId = ?
        #                 IF stock >= ?
        #             """,
        #             "Parameters":[
        #                 {"N": "1"},
        #                 {"S": "PROD#9"},
        #                 {"N": "1"}
        #             ]
        #         },
        #         {
        #             "Statement": """
        #                 INSERT INTO Orders VALUE {
        #                     'orderId': ?,
        #                     'userId': ?,
        #                     'amount': ?
        #                 }
        #             """,
        #             "Parameters": [
        #                 {"S": "ORD#1001"},
        #                 {"S": "user_123"},
        #                 {"N": "500"}
        #             ]
        #         }
        #     ]
        # )

        # def add_user(new_user: User):
        #     statement = "INSERT INTO " + TABLENAME + " VALUE {'PK': ?, 'SK': ?, 'email': ?, 'first_name': ?, 'flat': ?, 'id': ?, 'middle_name': ?, 'last_name': ?, 'mobile_number': ?, 'password': ?, 'role': ?}"

        #     try:
        #         dynamodb.execute_transaction(
        #             TransactStatements = [
        #                 {
        #                     "Statement": f"""
        #                         {statement}
        #                     """,
        #                     "Parameters": [
        #                         {"S": "USERS"},
        #                         {"S": f"{new_user.email}#{new_user.id}"},
        #                         {"S": f"{new_user.email}"},
        #                         {"S": f"{new_user.first_name}"},
        #                         {"S": f"{new_user.flat}"},
        #                         {"S": f"{new_user.id}"},
        #                         {"S": f"{new_user.middle_name}"},
        #                         {"S": f"{new_user.last_name}"},
        #                         {"S": f"{new_user.mobile_number}"},
        #                         {"S": f"{new_user.password}"},
        #                         {"S": f"{str(new_user.role)}"}
        #                     ]
        #                 },
        #                 {
        #                     "Statement": f"""
        #                         {statement}
        #                     """,
        #                     "Parameters": [
        #                         {"S": f"ROLE#{str(new_user.role)}"},
        #                         {"S": f"{new_user.id}"},
        #                         {"S": f"{new_user.email}"},
        #                         {"S": f"{new_user.first_name}"},
        #                         {"S": f"{new_user.flat}"},
        #                         {"S": f"{new_user.id}"},
        #                         {"S": f"{new_user.middle_name}"},
        #                         {"S": f"{new_user.last_name}"},
        #                         {"S": f"{new_user.mobile_number}"},
        #                         {"S": f"{new_user.password}"},
        #                         {"S": f"{str(new_user.role)}"}
        #                     ]
        #                 }
        #             ]
        #         )
        #     except Exception:
        #         raise Exception

    def get_user_by_email(self, email: str):
        statement = f"SELECT * FROM {self.table_name} WHERE PK = ? AND begins_with(SK, ?)"

        try:
            response = self.dynamodb.execute_statement(
                Statement=f"""
                    {statement}
                """,
                Parameters=[{"S": "USERS"}, {"S": email}],
            )
        except Exception:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Server Error")

        items = response["Items"]

        if len(items) == 0:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid Credentials")

        for item in items:
            user_details = {k: self.deserializer.deserialize(v) for k, v in item.items()}


        user: User = User(user_details.get("first_name"), user_details.get("middle_name"), 
                          user_details.get("last_name"), user_details.get("mobile_number"), user_details.get("email"), 
                          user_details.get("flat"), user_details.get("password"), user_details.get("role"), user_details.get("id"))

        return user
    
    


# def change_password(id, role, email, new_hashed_password):
#     statement = "UPDATE " + TABLENAME + " SET password = ? WHERE PK = ? AND SK = ?"

#     try:
#         dynamodb.execute_transaction(
#             TransactStatements = [
#                 {
#                     "Statement": f"""
#                         {statement}
#                     """,
#                     "Parameters": [
#                         {"S": f"{new_hashed_password}"},
#                         {"S": f"ROLE#{str(role)}"},
#                         {"S": f"{id}"}
#                     ]
#                 },
#                 {
#                     "Statement": f"""{statement}""",
#                     "Parameters": [
#                         {"S": f"{new_hashed_password}"},
#                         {"S": "USERS"},
#                         {"S": f"{email}#{id}"}
#                     ]
#                 }
#             ]
#         )
#     except Exception:
#         raise Exception
