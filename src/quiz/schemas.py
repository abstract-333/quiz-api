from pydantic import BaseModel


class QuizRead(BaseModel):
    resolve_time: int
    question: str
    choices: list
    answer: str
    type: str


class QuizCreate(BaseModel):
    resolve_time: int
    question: str
    choices: list
    answer: str
    added_by: str
    type: str