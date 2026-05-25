from app.services import embedder


class FakeEmbedding:
    def __init__(self, values: list[float]) -> None:
        self.values = values

    def tolist(self) -> list[float]:
        return self.values


class FakeEmbeddingBatch:
    def __init__(self, values: list[list[float]]) -> None:
        self.values = values

    def tolist(self) -> list[list[float]]:
        return self.values


class FakeModel:
    def encode(self, texts):
        if isinstance(texts, list):
            return FakeEmbeddingBatch([[float(len(text))] for text in texts])

        return FakeEmbedding([1.0, 2.0, 3.0])


def test_embed_text_returns_embedding(monkeypatch) -> None:
    monkeypatch.setattr(embedder, "get_embedding_model", lambda: FakeModel())

    assert embedder.embed_text("chunk text") == [1.0, 2.0, 3.0]


def test_embed_text_returns_empty_for_blank_text() -> None:
    assert embedder.embed_text("   ") == []


def test_embed_texts_returns_embeddings(monkeypatch) -> None:
    monkeypatch.setattr(embedder, "get_embedding_model", lambda: FakeModel())

    assert embedder.embed_texts(["one", "three"]) == [[3.0], [5.0]]
