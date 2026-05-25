from app.services.section_detector import detect_sections


def test_detect_sections_returns_requested_sections() -> None:
    text = """
Abstract
This is the abstract.

1 Introduction
This introduces the paper.

Related Work
This should not be included in the output.

2 Methodology
This explains the method.

Experiments
This should be a boundary only.

Results
These are the results.

Conclusion
This concludes the paper.

References
[1] Example reference.
"""

    assert detect_sections(text) == {
        "abstract": "This is the abstract.",
        "introduction": "This introduces the paper.",
        "methodology": "This explains the method.",
        "results": "These are the results.",
        "conclusion": "This concludes the paper.",
        "figures": [],
        "tables": [],
    }


def test_detect_sections_supports_heading_aliases() -> None:
    text = """
Methods
Method details.

Evaluation
Evaluation details.

Conclusions
Final thoughts.
"""

    sections = detect_sections(text)

    assert sections["methodology"] == "Method details."
    assert sections["results"] == "Evaluation details."
    assert sections["conclusion"] == "Final thoughts."


def test_detect_sections_extracts_figures_and_tables() -> None:
    text = """
Results
Figure 1: Model architecture overview.
The model improves accuracy.
Fig. 2. Training loss across epochs.
Table 1: Benchmark comparison.
Conclusion
Done.
"""

    sections = detect_sections(text)

    assert sections["figures"] == [
        "Figure 1: Model architecture overview.",
        "Fig. 2. Training loss across epochs.",
    ]
    assert sections["tables"] == ["Table 1: Benchmark comparison."]
