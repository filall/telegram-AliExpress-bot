from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config_data.config import DB_PATH
from app.logger import base_logger as logger

DATABASE_URL = DB_PATH

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)  # noqa
session = async_session()
Base = declarative_base()


async def create_models() -> None:
    logger.debug("Creating DB models")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown() -> None:
    logger.debug("Shutting down DB")
    await session.close()
    await engine.dispose()
