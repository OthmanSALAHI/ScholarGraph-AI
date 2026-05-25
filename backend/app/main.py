from fastapi import FastAPI
from app.api import chat, papers

app = FastAPI(title="ScholarGraph AI")

app.include_router(papers.router, prefix="/api/papers", tags=["Papers"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
