from pydantic import BaseModel


class RatingRead(BaseModel):
    questions_number: int
    solved: int


class RatingCreate(BaseModel):
    user_id: int
    university_id: int
    questions_number: int
    percent_solved: float


class RatingUpdate(BaseModel):
    questions_number: int
    percent_solved: float
