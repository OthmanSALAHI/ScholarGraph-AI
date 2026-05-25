from app.services.research_analyzer import analyze_paper


def test_analyze_paper_returns_structured_research_json() -> None:
    paper = {
        "filename": "script_switching_robustness.pdf",
        "sections": {
            "abstract": (
                "This study investigates robustness under script-switching attacks. "
                "The objective is to evaluate Arabic misinformation models [1]."
            ),
            "introduction": (
                "The problem is that Arabic NLP systems fail under Arabizi inputs. "
                "This creates an evaluation gap."
            ),
            "methodology": (
                "The study uses a controlled comparative experiment. "
                "Models are tested under Arabic and Arabizi script conditions."
            ),
            "results": (
                "The results confirm a large performance drop. "
                "The key finding is that robustness and accuracy differ [2, 3]."
            ),
            "conclusion": (
                "Only two architectures were evaluated. "
                "Future work should explore multi-script pre-training."
            ),
        },
    }

    analysis = analyze_paper(paper)

    assert analysis["title"] == "Script Switching Robustness"
    assert analysis["problem"] == (
        "The problem is that Arabic NLP systems fail under Arabizi inputs."
    )
    assert analysis["objective"] == (
        "This study investigates robustness under script-switching attacks."
    )
    assert analysis["method"] == (
        "The study uses a controlled comparative experiment. "
        "Models are tested under Arabic and Arabizi script conditions."
    )
    assert analysis["results"] == [
        "The results confirm a large performance drop.",
        "The key finding is that robustness and accuracy differ [2, 3].",
    ]
    assert analysis["limitations"] == ["Only two architectures were evaluated."]
    assert analysis["future_work"] == [
        "Future work should explore multi-script pre-training."
    ]
    assert analysis["citations"] == ["1", "2", "3"]
