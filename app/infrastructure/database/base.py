"""SQLAlchemy base"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so that Alembic can detect them when autogenerating migrations:
from app.infrastructure.database.models import item  # noqa: F401
from app.infrastructure.database.models import user  # noqa: F401
from app.infrastructure.database.models import refresh_token  # noqa: F401
