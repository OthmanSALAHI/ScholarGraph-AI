from pydantic import BaseModel


class ChatRequest(BaseModel):
    paper_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, object]]
