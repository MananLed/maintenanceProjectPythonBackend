from internal.repository import society_repository_instance

class SocietyService:
    def __init__(self):
        self.society_repository = society_repository_instance