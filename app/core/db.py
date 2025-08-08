from collections.abc import Generator

from sqlmodel import Session, create_engine, select
from supabase import create_client

from app.core.config import settings
from app.models import User

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_db() -> Generator[Session, None]:
    # This is a standard FastAPI dependency.
    # It opens a SQLAlchemy/SQLModel session to your Supabase database and automatically closes it after the request finishes.
    with Session(engine) as session:
        yield session


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel
    # # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    result = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER))
    user = result.first()
    if not user:
        super_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        response = super_client.auth.sign_up(
            {
                "email": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            }
        )
        assert response.user.email == settings.FIRST_SUPERUSER
        assert response.user.id is not None
        assert response.session.access_token is not None
