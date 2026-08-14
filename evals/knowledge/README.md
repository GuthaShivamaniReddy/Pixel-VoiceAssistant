# Knowledge evaluation

**Current scores:** produced by `pixel.knowledge.evaluate.evaluate` against `cases.jsonl` and the fixture corpus. Do not treat fluent wording as correctness.

Dataset: [`evals/knowledge/cases.jsonl`](cases.jsonl) (built by `python evals/knowledge/build_cases.py`).

Each case:

```text
id, question, category, expected_source, expected_behavior,
requires_current_information, expected_abstention, notes
```

Categories: organization overview, programs, audiences, training, career, educator, public-sector, business, contact, current information, dates/events, missing information, ambiguous, follow-up.

Run:

```bash
python -c "from pathlib import Path; from pixel.knowledge.evaluate import default_cases_path, evaluate, load_cases; print(evaluate(load_cases(default_cases_path())))"
```

Or pytest: `packages/pixel/tests/test_knowledge_eval.py`.
