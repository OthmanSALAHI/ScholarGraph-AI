from fastapi import APIRouter

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.retriever import retrieve_chunks

router = APIRouter()


@router.post("")
def chat_with_paper(request: ChatRequest) -> ChatResponse:
    chunks = retrieve_chunks(
        question=request.question,
        paper_id=request.paper_id,
    )

    if not chunks:
        return ChatResponse(
            answer="No relevant chunks found for this paper.",
            sources=[],
        )

    answer = "\n\n".join(str(chunk["text"]) for chunk in chunks if chunk.get("text"))
    return ChatResponse(answer=answer, sources=chunks)
