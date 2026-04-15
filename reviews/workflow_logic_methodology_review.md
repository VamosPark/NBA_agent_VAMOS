# NBA Agent VAMOS — Workflow/Logic Review

Date: 2026-04-15
Scope: Python scripts in `scripts/` and project markdown plans (`README.md`, `plan.md`, `workflow.plan.md`, `usage.md`).

---

## Executive Summary

The project has a strong analytical design in markdown, but implementation readiness is currently low because most pipeline functions are placeholders that raise `NotImplementedError`. The highest-priority workflow improvement is to move from a “phase narrative” workflow to an enforceable “artifact contract + stage-gate” workflow with explicit Definition of Done per phase.

---

## 1) Better Workflow Plan (Logic + Methodology)

## 1.1 Shift to an artifact-contract workflow

For each phase, define:
- **Input contract** (required files, required columns, dtypes, null policy)
- **Transformation contract** (deterministic operations + assumptions)
- **Output contract** (required output files + schema + quality thresholds)

Recommended gating order:
1. **Schema validation gate** at phase start.
2. **Computation gate** for core metrics.
3. **Quality gate** (distribution checks, missingness checks, range checks).
4. **Persistence gate** (write CSV/JSON + metadata + run hash).

Why: this prevents downstream execution on malformed intermediates and makes debugging reproducible.

## 1.2 Implement phase-level Definition of Done (DoD)

Suggested DoD template for each script:
- Script executes without `NotImplementedError`.
- Produces documented outputs in `data/` or `reports/`.
- Includes a dry-run mode (`--dry-run`) that validates contracts without full processing.
- Emits a summary report (row counts, null counts, key metric ranges).

## 1.3 Prioritize by dependency critical path

Critical path to first useful end-to-end run:
1. `ingest_bbref.py` (panel dataset)
2. `feature_engineering.py` (tool scores)
3. `clustering.py` (archetypes)
4. `salary_tiers.py` (final verdict)
5. `similarity.py` + `llm_narrative.py` (enrichment layers)

Rationale: this gets a minimally viable ranking/verdict pipeline first, then adds interpretability and synergy.

## 1.4 Add test strategy by layer

- **Unit tests**: formula-level logic (tier assignment boundaries, verdict mapping, season encoding).
- **Contract tests**: required columns and column types between phase outputs.
- **Smoke integration**: tiny fixture run through Phases 1→5 in CI.
- **Regression snapshots**: store expected summary stats (means/quantiles) to detect silent drift.

## 1.5 Make methodology assumptions machine-readable

Move these assumptions into versioned config where possible:
- Thresholds (`MIN_GP`, `MIN_MPG`, `LABEL_THRESHOLD`, tier cutoffs)
- Season-specific constants (league max salary)
- Data source precedence (Kaggle vs BBRef)

Why: changing assumptions should not require code edits; config diffs improve reviewability.

## 1.6 Operational workflow recommendation

Use a weekly workflow loop:
1. Refresh data sources.
2. Run full pipeline with run-id and timestamp.
3. Compare to previous run on top-line KPIs (cluster sizes, tier distributions, verdict deltas).
4. Publish markdown report summarizing deltas and anomalies.

---

## 2) Potential Weakness Tracker

| ID | Weakness | Severity | Evidence | Risk | Mitigation |
|---|---|---|---|---|---|
| W1 | Core scripts are unimplemented (`NotImplementedError`) | Critical | Most functions in pipeline stubs | No end-to-end output possible | Implement critical path scripts first; add smoke test gate |
| W2 | Documentation can be interpreted as runnable while pipeline is mostly stubbed | High | README quick-start commands vs implementation status | User confusion and failed runs | Add explicit project status badge + phase readiness matrix |
| W3 | Multiple season constants are hard-coded in code/docs | Medium | COVID seasons, league max values, thresholds | Silent stale logic across seasons | Move constants to `configs/*.yaml` + annual update checklist |
| W4 | Heavy dependence on external APIs/scraping without retry/cache policy | High | BBRef and nba_api ingestion design | Rate limits or provider changes break pipeline | Add request retry, exponential backoff, and raw-response caching |
| W5 | No explicit data quality checks on join keys (`player_id`, `season`, `team`) | High | Join-heavy multi-source architecture | Key collisions, duplicated rows, leakage | Add key uniqueness tests and merge diagnostics by phase |
| W6 | Synergy formula is conceptually strong but sample-size fragility remains | Medium | Requires pair/solo minutes thresholds | High variance estimates for sparse pairs | Add confidence intervals / shrinkage estimator |
| W7 | LLM fallback labeling is under-specified for reproducibility | Medium | Threshold-triggered naming path | Label instability run-to-run | Store prompts, model version, and deterministic temperature |
| W8 | No explicit observability/lineage output | Medium | No run metadata artifact specified | Hard postmortem/debugging | Write `reports/run_metadata.json` (inputs hash, config hash, versions) |

---

## 3) Immediate Next Actions (Two-Week Plan)

### Week 1 (stabilize execution)
- Implement `ingest_bbref.py` and `feature_engineering.py` with schema gates.
- Add minimal fixtures and smoke test (`tests/test_smoke_pipeline.py`).
- Add `--dry-run` to all scripts.

### Week 2 (decision-quality outputs)
- Implement `clustering.py` and `salary_tiers.py` fully.
- Add run metadata logging and quality reports.
- Freeze v1 config contracts for thresholds and season constants.

---

## 4) Review Method

This review used static inspection of repository scripts and markdown design docs, emphasizing workflow enforceability, dependency ordering, reproducibility, and risk exposure.
