from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "postgresql://dev:dev123@localhost:5432/internal_tools"


engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


def get_db():
    """Dependency for getting a database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
