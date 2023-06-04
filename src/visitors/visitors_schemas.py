from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP

from auth.auth_models import user
from database import Base
from university.university_models import university


class VisitorsWrite(BaseModel):
    country: str
    count: int
