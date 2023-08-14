from api.university.university_schames import University
from core.repository import SQLAlchemyRepository


class UniversityRepository(SQLAlchemyRepository):
    main_model = University
