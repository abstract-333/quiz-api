from api.university.university_schames import University
from common.sqlalchemy_repository import SQLAlchemyRepository


class UniversityRepository(SQLAlchemyRepository):
    model = University
