import pytest

from app.db import vector_store


class FakeCollection:
    def __init__(self) -> None:
        self.add_calls = []
        self.query_calls = []

    def add(self, **kwargs) -> None:
        self.add_calls.append(kwargs)

    def query(self, **kwargs) -> dict:
        self.query_calls.append(kwargs)
        return {"ids": [["paper_001_chunk_001"]]}


def test_store_chunks_adds_text_embeddings_and_metadata(monkeypatch) -> None:
    collection = FakeCollection()
    monkeypatch.setattr(
        vector_store,
        "get_chroma_collection",
        lambda persist_directory, collection_name: collection,
    )

    vector_store.store_chunks(
        chunks=[
            {
                "chunk_id": "paper_001_chunk_001",
                "paper_id": "paper_001",
                "section": "methodology",
                "text": "Method text.",
                "page": 5,
            }
        ],
        embeddings=[[0.1, 0.2]],
    )

    assert collection.add_calls == [
        {
            "ids": ["paper_001_chunk_001"],
            "documents": ["Method text."],
            "embeddings": [[0.1, 0.2]],
            "metadatas": [
                {
                    "paper_id": "paper_001",
                    "section": "methodology",
                    "page": 5,
                }
            ],
        }
    ]


def test_store_chunks_rejects_embedding_count_mismatch() -> None:
    with pytest.raises(ValueError):
        vector_store.store_chunks(
            chunks=[
                {
                    "chunk_id": "paper_001_chunk_001",
                    "paper_id": "paper_001",
                    "section": "methodology",
                    "text": "Method text.",
                    "page": 5,
                }
            ],
            embeddings=[],
        )


def test_search_chunks_queries_collection(monkeypatch) -> None:
    collection = FakeCollection()
    monkeypatch.setattr(
        vector_store,
        "get_chroma_collection",
        lambda persist_directory, collection_name: collection,
    )

    results = vector_store.search_chunks([0.1, 0.2], limit=3, paper_id="paper_001")

    assert results == {"ids": [["paper_001_chunk_001"]]}
    assert collection.query_calls == [
        {
            "query_embeddings": [[0.1, 0.2]],
            "n_results": 3,
            "where": {"paper_id": "paper_001"},
        }
    ]
