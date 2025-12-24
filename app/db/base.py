from sqlalchemy.orm import DeclarativeBase

# IMPORTANT: import models so Alembic sees them

class Base(DeclarativeBase):
    pass
