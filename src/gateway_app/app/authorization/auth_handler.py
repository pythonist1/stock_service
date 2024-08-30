from abstractions import AbstractUserRepository


class AuthHandler:
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    async def get_user_id(self, name: str) -> int:
        return await self.user_repository.get_user_id(name)
