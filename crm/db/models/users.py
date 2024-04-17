from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from rsouvenir_crm.db.dependencies import get_db_session

class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)