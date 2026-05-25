from app.db.vector_store import search_chunks
from app.services.embedder import embed_text


RetrievedChunk = dict[str, object]


def retrieve_chunks(
    question: str,
    paper_id: str | None = None,
    limit: int = 5,
) -> list[RetrievedChunk]:
    query_embedding = embed_text(question)
    if not query_embedding:
        return []

    results = search_chunks(query_embedding, limit=limit, paper_id=paper_id)
    return _format_results(results)


def _format_results(results: dict) -> list[RetrievedChunk]:
    ids = _first_result_group(results.get("ids"))
    documents = _first_result_group(results.get("documents"))
    metadatas = _first_result_group(results.get("metadatas"))
    distances = _first_result_group(results.get("distances"))

    chunks: list[RetrievedChunk] = []
    for index, chunk_id in enumerate(ids):
        metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": documents[index] if index < len(documents) else "",
                "paper_id": metadata.get("paper_id"),
                "section": metadata.get("section"),
                "page": metadata.get("page"),
                "score": distances[index] if index < len(distances) else None,
            }
        )

    return chunks


def _first_result_group(value: object) -> list:
    if not isinstance(value, list) or not value:
        return []

    first = value[0]
    return first if isinstance(first, list) else value
