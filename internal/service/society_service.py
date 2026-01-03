from internal.repository import society_repository_instance
from fastapi import HTTPException
from internal.models.user import UserRole

class SocietyService:
    def __init__(self):
        self.society_repository = society_repository_instance

    async def get_all_users_by_role(self, role: UserRole):
        try:
            users = await self.society_repository.get_all_users_by_role(role)
        except HTTPException as exception:
            raise exception 
        except Exception as exception:
            raise exception
        
        return users