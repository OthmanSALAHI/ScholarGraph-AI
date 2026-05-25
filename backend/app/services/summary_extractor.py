import re


def extract_problem(sections: dict[str, object]) -> str:
    return _find_sentence(
        _section_text(sections, "introduction"),
        ["problem", "challenge", "gap", "fails", "absence", "risk"],
    ) or _first_sentence(_section_text(sections, "abstract"))


def extract_objective(sections: dict[str, object]) -> str:
    return _find_sentence(
        _section_text(sections, "abstract"),
        ["study investigates", "this work", "we investigate", "objective", "aim"],
    ) or _find_sentence(
        _section_text(sections, "introduction"),
        ["contribution", "study", "evaluate", "investigate"],
    )


def extract_method(sections: dict[str, object]) -> str:
    return _first_sentences(_section_text(sections, "methodology"), limit=2)


def extract_results(sections: dict[str, object]) -> list[str]:
    return _find_sentences(
        _section_text(sections, "results"),
        ["result", "finding", "confirm", "drop", "improve", "decrease", "increase"],
        limit=5,
    )


def extract_limitations(sections: dict[str, object]) -> list[str]:
    result_text = _section_text(sections, "results")
    conclusion_text = _section_text(sections, "conclusion")
    return _find_sentences(
        f"{result_text}\n{conclusion_text}",
        ["limitation", "limited", "only", "not capture"],
        limit=5,
    )


def extract_future_work(sections: dict[str, object]) -> list[str]:
    return _find_sentences(
        _section_text(sections, "conclusion"),
        ["future", "should", "explore", "improve"],
        limit=5,
    )


def _section_text(sections: dict[str, object], section: str) -> str:
    value = sections.get(section, "")
    return value if isinstance(value, str) else ""


def _find_sentence(text: str, keywords: list[str]) -> str:
    sentences = _find_sentences(text, keywords, limit=1)
    return sentences[0] if sentences else ""


def _find_sentences(text: str, keywords: list[str], limit: int) -> list[str]:
    matches: list[str] = []
    for sentence in _split_sentences(text):
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            matches.append(sentence)
            if len(matches) == limit:
                break

    return matches


def _first_sentence(text: str) -> str:
    sentences = _split_sentences(text)
    return sentences[0] if sentences else ""


def _first_sentences(text: str, limit: int) -> str:
    return " ".join(_split_sentences(text)[:limit])


def _split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", normalized)
        if sentence.strip()
    ]
