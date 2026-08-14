from pixel.knowledge.evaluate import default_cases_path, evaluate, load_cases
from pixel.knowledge.runtime import fixture_retriever


def test_knowledge_evaluation_dataset_and_baseline() -> None:
    path = default_cases_path()
    assert path.is_file(), "evals/knowledge/cases.jsonl is required"
    cases = load_cases(path)
    assert len(cases) >= 100
    categories = {str(case["category"]) for case in cases}
    required = {
        "organization_overview",
        "programs",
        "target_audiences",
        "training",
        "career_resources",
        "educator_resources",
        "public_sector_resources",
        "business_resources",
        "contact_resources",
        "current_information",
        "dates_events",
        "missing_information",
        "ambiguous",
        "follow_up",
    }
    assert required <= categories
    metrics = evaluate(cases, retriever=fixture_retriever())
    assert metrics["retrieval_case_count"] > 0
    assert metrics["abstention_case_count"] > 0
    assert metrics["hit_at_5"] >= 0.5
    assert metrics["abstention"] >= 0.7
    assert metrics["groundedness"] >= 0.5
