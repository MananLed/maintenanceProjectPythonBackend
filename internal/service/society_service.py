from internal.repository import society_repository_instance
from fastapi import HTTPException
from internal.models.user import UserRole
from uuid import UUID

class SocietyService:
    def __init__(self):
        self.society_repository = society_repository_instance

    async def get_all_users_by_role(self, role: UserRole):
        
        users = await self.society_repository.get_all_users_by_role(role)
        
        return users
    
    async def delete_user(self, id: UUID, role: UserRole):

        await self.society_repository.delete_user(id, role)