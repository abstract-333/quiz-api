from typing import Optional

from pydantic import BaseModel


class FeedbackRead(BaseModel):
    rating: int
    feedback_title: str
    question_id: int


class FeedbackCreate(BaseModel):
    rating: int
    feedback_title: str
    user_id: int
    question_id: int
