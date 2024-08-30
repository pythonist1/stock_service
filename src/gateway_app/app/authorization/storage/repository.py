from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert
from authorization.exceptions import DatabaseError
from abstractions import AbstractUserRepository


class UserRepository(AbstractUserRepository):
    def __init__(self, engine: AsyncEngine, db_tables):
        self._engine = engine
        self._db_tables = db_tables

    async def get_user_id(self, name: str) -> int:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                try:
                    result = await session.execute(select(self._db_tables.User).filter_by(name=name))
                    db_user = result.scalar_one_or_none()

                    if db_user:
                        return db_user.id

                    stmt = insert(self._db_tables.User).values(name=name).returning(self._db_tables.User.id)
                    result = await session.execute(stmt)
                    new_user_id = result.scalar()

                    return new_user_id

                except SQLAlchemyError as e:
                    await session.rollback()
                    raise DatabaseError(f"Database error: {e}")
