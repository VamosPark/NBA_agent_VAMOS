# NBA Player Performance Analysis

A bottom-up NBA analytics pipeline that evaluates player performance, groups
players into skill-based archetypes, measures pair synergy, and renders a
salary justification verdict for every player in the league.

See **`plan.md`** for the full project design (v3.0) and **`workflow.plan.md`**
for the skill-tool layering and synergy refinement addendum.

## Quick start (once data is collected)

```bash
pip install -r requirements.txt

# Phase 1 — pull data
python scripts/ingest_bbref.py --start-season 2019 --end-season 2025
python scripts/ingest_nba_api.py
python scripts/ingest_salary.py

# Phase 2 — feature engineering + tool scores
python scripts/feature_engineering.py

# Phase 3 — clustering
python scripts/clustering.py

# Phase 4 — similarity + synergy
python scripts/similarity.py

# Phase 5 — salary evaluation
python scripts/salary_tiers.py
```

## LLM runtime

Narrative generation targets a local Ollama endpoint
(`http://localhost:11434/v1`). Model: TBD (Gemma family).
No cloud API keys required.
