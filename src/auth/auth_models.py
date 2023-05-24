from datetime import datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from section.section_models import section
from university.university_models import university

metadata = MetaData()

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(length=25), nullable=False),
    Column("permissions", JSON),
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(length=50), nullable=False, index=True, unique=True),
    Column("username", String(length=25), nullable=False),
    Column("role_id", Integer, ForeignKey(role.c.id), nullable=False),
    Column("university_id", Integer, ForeignKey(university.c.id), nullable=True),
    Column("section_id", Integer, ForeignKey(section.c.id), nullable=True),
    Column("phone", String(length=10), nullable=True),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("hashed_password", String(length=128), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)


class User(SQLAlchemyBaseUserTable[int], Base):
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    email = Column(String(length=50), nullable=False, index=True)
    username = Column(String(length=25), nullable=False)
    role_id = Column(Integer, ForeignKey(role.c.id))
    section_id = Column(Integer, ForeignKey(section.c.id), nullable=True)
    phone = Column(String(length=10), nullable=True)
    university_id = Column(Integer, ForeignKey(university.c.id), nullable=True)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow())
    hashed_password: Mapped[str] = mapped_column(String(length=128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
