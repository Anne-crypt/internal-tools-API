import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base
from app.models.category import Category
from app.models.tool import Tool
from sqlalchemy import delete

# Database de test en mémoire
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure le backend pour les tests asynchrones."""
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def initialize_db():
    """Crée les tables au début de la session et les détruit à la fin."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session de base de données propre pour chaque fonction de test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def seed_data(db_session: AsyncSession):
    """Insère des données de test de base."""
    # Nettoyage anti-duplication pour SQLite
    await db_session.execute(delete(Tool))
    await db_session.execute(delete(Category))
    await db_session.commit()

    # 1. Création des catégories
    cat_dev = Category(name="Development", color_hex="#111111")
    cat_comm = Category(name="Communication", color_hex="#222222")
    db_session.add_all([cat_dev, cat_comm])
    await db_session.commit()

    # 2. Création des outils
    t1 = Tool(
        name="Slack",
        vendor="Slack Tech",
        category_id=cat_comm.id,
        monthly_cost=8.00,
        owner_department="Engineering",
        status="active",
        active_users_count=25,
    )
    t2 = Tool(
        name="Jira",
        vendor="Atlassian",
        category_id=cat_dev.id,
        monthly_cost=45.00,
        owner_department="Engineering",
        status="active",
        active_users_count=10,
    )
    t3 = Tool(
        name="Zoom",
        vendor="Zoom Video",
        category_id=cat_comm.id,
        monthly_cost=15.00,
        owner_department="Sales",
        status="deprecated",
        active_users_count=5,
    )

    db_session.add_all([t1, t2, t3])
    await db_session.commit()
