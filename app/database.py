from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://dev:dev123@localhost:5432/internal_tools"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


async def get_db():
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
