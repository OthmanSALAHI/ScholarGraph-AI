from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import generate_answer
from app.services.retriever import retrieve_chunks

router = APIRouter()


@router.post("")
def chat_with_paper(request: ChatRequest) -> ChatResponse:
    paper_id = normalize_paper_id(request.paper_id)

    try:
        chunks = retrieve_chunks(
            question=request.question,
            paper_id=paper_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not chunks:
        return ChatResponse(
            answer="No relevant chunks found for this paper.",
            sources=[],
        )

    try:
        answer = generate_answer(request.question, chunks)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(answer=answer, sources=chunks)


def normalize_paper_id(paper_id: str) -> str:
    if Path(paper_id).suffix.lower() == ".pdf":
        return Path(paper_id).stem

    return paper_id
