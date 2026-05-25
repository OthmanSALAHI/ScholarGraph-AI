from app.services import llm_service


class FakeMessage:
    content = "Generated answer."


class FakeChoice:
    message = FakeMessage()


class FakeResponse:
    choices = [FakeChoice()]


class FakeCompletions:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs) -> FakeResponse:
        self.calls.append(kwargs)
        return FakeResponse()


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeCompletions()


class FakeClient:
    def __init__(self) -> None:
        self.chat = FakeChat()


def test_generate_answer_uses_question_context_and_github_model(monkeypatch) -> None:
    client = FakeClient()
    monkeypatch.setattr(llm_service, "get_llm_client", lambda: client)

    answer = llm_service.generate_answer(
        question="What problem does this paper solve?",
        chunks=[
            {
                "chunk_id": "paper_001_chunk_001",
                "paper_id": "paper_001",
                "section": "abstract",
                "text": "It solves research paper retrieval.",
                "page": 1,
            }
        ],
    )

    assert answer == "Generated answer."
    call = client.chat.completions.calls[0]
    assert call["model"] == "openai/gpt-4o"
    assert call["temperature"] == 0.2
    assert "Use only the provided context" in call["messages"][0]["content"]
    assert "What problem does this paper solve?" in call["messages"][1]["content"]
    assert "[abstract, page 1]" in call["messages"][1]["content"]
    assert "It solves research paper retrieval." in call["messages"][1]["content"]


def test_generate_answer_returns_unknown_without_context() -> None:
    assert llm_service.generate_answer("Question?", []) == (
        "I don't know based on the provided context."
    )


def test_load_env_files_loads_project_root_before_backend_env(monkeypatch) -> None:
    loaded_paths = []

    def fake_load_dotenv(path, override):
        loaded_paths.append((path.name, override))

    llm_service._load_env_files(fake_load_dotenv)

    assert loaded_paths == [
        (".env", True),
        (".env", True),
    ]
