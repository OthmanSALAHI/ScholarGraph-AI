from pathlib import Path
from typing import TypedDict


CHROMA_DB_DIR = "chroma_db"
COLLECTION_NAME = "paper_chunks"


class VectorChunk(TypedDict):
    chunk_id: str
    paper_id: str
    section: str
    text: str
    page: int | None


def get_chroma_collection(
    persist_directory: str | Path = CHROMA_DB_DIR,
    collection_name: str = COLLECTION_NAME,
):
    try:
        import chromadb
    except ModuleNotFoundError as exc:
        raise RuntimeError("chromadb is required for local vector storage.") from exc

    client = chromadb.PersistentClient(path=str(persist_directory))
    return client.get_or_create_collection(name=collection_name)


def store_chunks(
    chunks: list[VectorChunk],
    embeddings: list[list[float]],
    persist_directory: str | Path = CHROMA_DB_DIR,
    collection_name: str = COLLECTION_NAME,
) -> None:
    if not chunks:
        return

    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length.")

    collection = get_chroma_collection(persist_directory, collection_name)
    collection.add(
        ids=[chunk["chunk_id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embeddings,
        metadatas=[_chunk_metadata(chunk) for chunk in chunks],
    )


def search_chunks(
    query_embedding: list[float],
    limit: int = 5,
    paper_id: str | None = None,
    persist_directory: str | Path = CHROMA_DB_DIR,
    collection_name: str = COLLECTION_NAME,
) -> dict:
    collection = get_chroma_collection(persist_directory, collection_name)
    query_kwargs: dict[str, object] = {
        "query_embeddings": [query_embedding],
        "n_results": limit,
    }

    if paper_id:
        query_kwargs["where"] = {"paper_id": paper_id}

    return collection.query(**query_kwargs)


def _chunk_metadata(chunk: VectorChunk) -> dict[str, object]:
    metadata: dict[str, object] = {
        "paper_id": chunk["paper_id"],
        "section": chunk["section"],
    }

    if chunk["page"] is not None:
        metadata["page"] = chunk["page"]

    return metadata
