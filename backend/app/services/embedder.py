from functools import lru_cache


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "sentence-transformers is required to create embeddings."
        ) from exc

    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    if not text.strip():
        return []

    embedding = get_embedding_model().encode(text)
    return embedding.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = get_embedding_model().encode(texts)
    return embeddings.tolist()
