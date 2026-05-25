import os
from functools import lru_cache
from pathlib import Path

from app.services.retriever import RetrievedChunk


GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
GITHUB_MODELS_MODEL = "openai/gpt-4o"


@lru_cache(maxsize=1)
def get_llm_client():
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError as exc:
        raise RuntimeError("python-dotenv is required to load environment variables.") from exc

    _load_env_files(load_dotenv)
    token = (os.getenv("GITHUB_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required to generate LLM answers.")

    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("openai is required to generate LLM answers.") from exc

    return OpenAI(
        base_url=GITHUB_MODELS_ENDPOINT,
        api_key=token,
    )


def _load_env_files(load_dotenv) -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    project_root = backend_dir.parent

    load_dotenv(project_root / ".env", override=True)
    load_dotenv(backend_dir / ".env", override=True)


def generate_answer(
    question: str,
    chunks: list[RetrievedChunk],
    model_name: str = GITHUB_MODELS_MODEL,
) -> str:
    if not chunks:
        return "I don't know based on the provided context."

    context = _format_context(chunks)
    try:
        response = get_llm_client().chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Use only the provided context. "
                        "Answer clearly. "
                        "Mention section/page if available. "
                        "If the answer is not in the context, say you don't know."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Context:\n{context}"
                    ),
                },
            ],
            temperature=0.2,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
        )
    except Exception as exc:
        raise RuntimeError(f"LLM answer generation failed: {exc}") from exc

    return response.choices[0].message.content


def _format_context(chunks: list[RetrievedChunk]) -> str:
    context_blocks: list[str] = []
    for chunk in chunks:
        section = chunk.get("section") or "unknown section"
        page = chunk.get("page")
        page_text = f"page {page}" if page is not None else "page unknown"
        text = chunk.get("text") or ""
        context_blocks.append(f"[{section}, {page_text}]\n{text}")

    return "\n\n".join(context_blocks)
