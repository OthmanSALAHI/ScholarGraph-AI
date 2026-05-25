from pydantic import BaseModel


class Paper(BaseModel):
    id: str | None = None
    title: str
    abstract: str | None = None