from api.university.university_schames import University
from common.repository import SQLAlchemyRepository


class UniversityRepository(SQLAlchemyRepository):
    model = University
