from pydantic import BaseModel


class SectionSchema(BaseModel):
    id: int
    name: str


