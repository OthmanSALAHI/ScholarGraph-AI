from app.services.citation_extractor import extract_citations
from app.services.metadata_extractor import extract_title
from app.services.summary_extractor import (
    extract_future_work,
    extract_limitations,
    extract_method,
    extract_objective,
    extract_problem,
    extract_results,
)


ResearchAnalysis = dict[str, object]


def analyze_paper(paper: dict[str, object]) -> ResearchAnalysis:
    sections = paper.get("sections", {})
    if not isinstance(sections, dict):
        sections = {}

    full_text = "\n".join(value for value in sections.values() if isinstance(value, str))

    return {
        "title": extract_title(paper),
        "problem": extract_problem(sections),
        "objective": extract_objective(sections),
        "method": extract_method(sections),
        "results": extract_results(sections),
        "limitations": extract_limitations(sections),
        "future_work": extract_future_work(sections),
        "citations": extract_citations(full_text),
    }
