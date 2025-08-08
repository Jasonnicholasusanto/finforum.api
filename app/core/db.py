from collections.abc import Generator
from sqlmodel import Session, create_engine
from app.core.config import settings


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_db() -> Generator[Session, None]:
    # This is a standard FastAPI dependency.
    # It opens a SQLAlchemy/SQLModel session to your Supabase database and automatically closes it after the request finishes.
    with Session(engine) as session:
        yield session

