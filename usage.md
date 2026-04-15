# Usage Guide

End-to-end instructions for running the NBA Player Performance Analysis pipeline.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Configuration Files](#2-configuration-files)
3. [Data Prerequisites](#3-data-prerequisites)
4. [Phase-by-Phase CLI Reference](#4-phase-by-phase-cli-reference)
   - [Phase 1 — Data Ingestion](#phase-1--data-ingestion)
   - [Phase 2 — Feature Engineering](#phase-2--feature-engineering)
   - [Phase 3 — Clustering](#phase-3--clustering)
   - [Phase 4 — Similarity & Synergy](#phase-4--similarity--synergy)
   - [Phase 5 — Salary Evaluation](#phase-5--salary-evaluation)
   - [LLM Layer — Narrative Generation](#llm-layer--narrative-generation)
5. [Running Notebooks](#5-running-notebooks)
6. [LLM (Ollama) Setup](#6-llm-ollama-setup)
7. [Data Flow Diagram](#7-data-flow-diagram)
8. [Output Files Reference](#8-output-files-reference)

---

## 1. Environment Setup

```bash
# Clone and enter the repo
git clone https://github.com/vamospark/nba_agent_vamos.git
cd NBA_agent_VAMOS

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Python version:** 3.11+ recommended (type hints use `dict[str, ...]` syntax).

**Optional — copy environment template:**

```bash
cp .env.example .env             # then edit .env with your values
```

`.env` variables (all optional — sensible defaults apply):

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama API endpoint |
| `OLLAMA_MODEL` | `gemma:4b` | Local model name |

---

## 2. Configuration Files

Two YAML files control the analytical logic. Edit these before running the pipeline.

### `configs/tool_mapping.yaml`

Defines the 17 **Tools** (scouting abilities) and how they are computed from
raw stats. Each tool specifies:
- `stats` — raw column names from `nba_panel_raw.csv`
- `weights` — per-stat weight (negative = inverse, e.g. TOV_pct)
- `aggregation` — `weighted_z` or `custom` formula

Example entry:

```yaml
tools:
  shooting_ability:
    stats: [TS_pct, eFG_pct, FG3_pct, FT_pct]
    weights: [0.40, 0.30, 0.20, 0.10]
    aggregation: weighted_z
```

### `configs/player_types.yaml`

Defines the 7 **player archetypes** used for cluster labeling:
`primary_creator`, `shooter`, `defensive_anchor`, `two_way_wing`,
`playmaking_big`, `rebounding_big`, `role_connector`.

Each archetype has `key_features` (tools that define it) and `anti_features`
(tools it typically lacks). Cluster centroids are matched to archetypes by
cosine similarity (threshold: **0.60**). Below threshold → LLM names the cluster.

---

## 3. Data Prerequisites

The following files must be present **before** running the pipeline.
Phase 1 scripts generate most of them; the Kaggle file is a manual download.

| File | Source | Required by |
|---|---|---|
| `data/salaries_raw.csv` | [Kaggle NBA Salaries](https://www.kaggle.com/datasets/erikvdven/nba-salaries) — manual download | `ingest_salary.py` |

All other `data/` files are created by the pipeline itself.

---

## 4. Phase-by-Phase CLI Reference

> **Status:** All scripts are currently stubs — they raise `NotImplementedError`.
> Run them only after the corresponding implementation is complete.
> Each section notes which functions remain unimplemented.

---

### Phase 1 — Data Ingestion

Run the three ingestion scripts in any order; they produce independent outputs.

#### 1a. Basketball-Reference stats

```bash
python scripts/ingest_bbref.py \
    --start-season 2019 \
    --end-season 2025 \
    --out data/nba_panel_raw.csv
```

| Flag | Default | Description |
|---|---|---|
| `--start-season` | `2019` | First season end-year to pull |
| `--end-season` | `2025` | Last season end-year to pull |
| `--out` | `data/nba_panel_raw.csv` | Output CSV path |

**Season encoding:** end-year integer — `2025` means the 2024-25 season.

**Rate limiting:** 3.5 s sleep between seasons (~30 s total for 7 seasons).

**Not yet implemented:** `fetch_season_pergame`, `fetch_season_advanced`,
`merge_pergame_advanced`, `build_panel`.

---

#### 1b. NBA.com lineup + on/off data

```bash
python scripts/ingest_nba_api.py \
    --seasons 2022 2023 2024 2025 \
    --out-lineups data/lineup_raw.csv \
    --out-onoff   data/onoff_raw.csv
```

| Flag | Default | Description |
|---|---|---|
| `--seasons` | `2022 2023 2024 2025` | Space-separated list of season end-years |
| `--out-lineups` | `data/lineup_raw.csv` | 2-man lineup output |
| `--out-onoff` | `data/onoff_raw.csv` | Per-player on/off output |

**Rate limiting:** 0.6 s sleep between API calls.

**Not yet implemented:** `fetch_lineup_data`, `fetch_onoff_data`.

---

#### 1c. Salary data

Place the Kaggle CSV at `data/salaries_raw.csv`, then:

```bash
python scripts/ingest_salary.py
```

Output is always written to `data/salary_panel.csv`.

**Not yet implemented:** `load_kaggle_salaries`, `scrape_bbref_contracts`.
`normalize_salaries` and `assign_salary_tier` are already implemented.

---

### Phase 2 — Feature Engineering

Requires: `data/nba_panel_raw.csv`, `configs/tool_mapping.yaml`

```bash
python scripts/feature_engineering.py
```

Outputs:
- `data/nba_longitudinal_features.csv` — rolling averages, trajectory slope,
  consistency score, career phase, peak BPM
- `data/nba_tool_scores.csv` — one `tool_*` column per tool per player-season

**Minimum sample filter:** GP ≥ 20 AND MPG ≥ 15.
Players with GP < 50 are flagged `injury_flag = True` but kept.

**COVID weighting:** seasons 2020 and 2021 are weighted 0.7× in rolling averages.

**Not yet implemented:** all functions except module constants.

---

### Phase 3 — Clustering

Requires: `data/nba_tool_scores.csv`, `configs/player_types.yaml`

```bash
python scripts/clustering.py
```

Outputs:
- `data/nba_archetypes.csv` — original rows + `cluster_id`, `player_type_label`,
  `player_type_similarity`, `llm_named`
- `reports/cluster_profiles.json` — centroid stats + label + top players per cluster

**PCA:** selects components that explain ≥ 80% cumulative variance.

**K-Means:** tests k = 6 to 10; picks best k by silhouette score.

**Labeling:** cosine similarity of centroid to player_type key_feature vectors.
Threshold 0.60 — below this, `llm_named = True` and `interpret_cluster()` is called.

**Not yet implemented:** `load_tool_scores`, `run_pca`, `select_best_k`,
`build_player_type_vectors`, `label_cluster`, `generate_cluster_profiles`.

---

### Phase 4 — Similarity & Synergy

Requires: `data/nba_archetypes.csv`, `data/lineup_raw.csv`, `data/onoff_raw.csv`,
`configs/player_types.yaml`

```bash
python scripts/similarity.py
```

Outputs:
- `data/player_similarity.csv` — top 10 most similar player-seasons per player
- `data/lineup_synergy.csv` — pair-level synergy scores

**Similarity method:** cosine similarity on PCA component scores.

**Synergy formula** (interaction-effect, isolates the pair interaction):

```
interaction_effect(A, B | team) =
    NetRtg_on(A+B on court)
  − NetRtg_off(neither A nor B)          ← team baseline
  − [NetRtg_on(A without B) − NetRtg_off]  ← A's solo lift
  − [NetRtg_on(B without A) − NetRtg_off]  ← B's solo lift
```

Minimum sample: 100 shared minutes for the pair, 100 solo minutes for each player.
Pairs below the solo threshold fall back to archetype complementarity (`synergy_proxy = True`).

**Team context tier:** quintile of `team_baseline_netrtg` relative to all teams
in the same season (T1 = top 20%, T5 = bottom 20%).

**Not yet implemented:** all functions.

---

### Phase 5 — Salary Evaluation

Requires: `data/nba_archetypes.csv`, `data/nba_longitudinal_features.csv`,
`data/salary_panel.csv`, `data/lineup_synergy.csv`

```bash
python scripts/salary_tiers.py
```

Output: `data/nba_salary_evaluation.csv`

Columns: `player_id | player_name | season | player_type_label | career_phase |
rank_score | within_archetype_rank | league_rank | perf_tier | salary_tier |
delta_tier | verdict`

**Ranking formula** (within-archetype percentile):
```
rank_score = 0.40 × WS_48_pct + 0.35 × BPM_pct + 0.25 × VORP_pct
```

**Performance tiers** (within-archetype rank_score percentile):

| Tier | Percentile | Label |
|---|---|---|
| T1 | top 10% | Franchise-level |
| T2 | 10–30% | All-Star caliber |
| T3 | 30–60% | Solid starter |
| T4 | 60–80% | Rotation player |
| T5 | bottom 20% | Fringe / bench |

**Salary tiers** (`pct_league_max`):

| Tier | Range | Label |
|---|---|---|
| T1 | > 0.85 | Supermax / Max |
| T2 | 0.60–0.85 | Near-max |
| T3 | 0.35–0.60 | Mid-level range |
| T4 | 0.15–0.35 | Role player deal |
| T5 | < 0.15 | Minimum / two-way |

**Verdict** (Delta = Salary_Tier − Performance_Tier):

| Delta | Verdict |
|---|---|
| ≥ +2 | SIGNIFICANTLY OVERPAID |
| +1 | OVERPAID |
| 0 | FAIR VALUE |
| −1 | UNDERPAID |
| ≤ −2 | SIGNIFICANTLY UNDERPAID |

**Not yet implemented:** `compute_within_archetype_percentiles`,
`compute_rank_score`, `assign_perf_tier`. `assign_salary_tier` and
`compute_verdict` are already implemented.

---

### LLM Layer — Narrative Generation

The narrative module is called **from within** `clustering.py` (Layer A)
and `salary_tiers.py` (Layer B). It is not invoked directly via CLI.

To configure the local model, set environment variables before running either
pipeline script:

```bash
export OLLAMA_BASE_URL="http://localhost:11434/v1"   # default
export OLLAMA_MODEL="gemma:4b"                        # or gemma:27b, etc.

python scripts/clustering.py    # triggers Layer A for unnamed clusters
python scripts/salary_tiers.py  # triggers Layer B for all player cards
```

**Not yet implemented:** `_get_client`, `interpret_cluster`, `generate_player_card`.

---

## 5. Running Notebooks

Notebooks provide an interactive walkthrough of each phase. They call the same
scripts internally once implemented.

```bash
pip install jupyter
jupyter lab
```

| Notebook | Phase | Script it exercises |
|---|---|---|
| `01_data_collection.ipynb` | Phase 1 | `ingest_bbref.py`, `ingest_nba_api.py`, `ingest_salary.py` |
| `02_feature_engineering.ipynb` | Phase 2 | `feature_engineering.py` |
| `03_pca_clustering.ipynb` | Phase 3 | `clustering.py` |
| `04_similarity_synergy.ipynb` | Phase 4 | `similarity.py` |
| `05_salary_evaluation.ipynb` | Phase 5 | `salary_tiers.py`, `llm_narrative.py` |

---

## 6. LLM (Ollama) Setup

The pipeline uses a **local** OpenAI-compatible endpoint — no API keys required.

```bash
# Install Ollama  (https://ollama.com)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model (choose one)
ollama pull gemma:4b       # fast, lower RAM (~3 GB)
ollama pull gemma:27b      # higher quality (~17 GB)
ollama pull llama3.2:3b    # alternative

# Start the server (runs on port 11434 by default)
ollama serve
```

Verify it is reachable:

```bash
curl http://localhost:11434/v1/models
```

The pipeline reads `OLLAMA_MODEL` from the environment; update it if you
pulled a different model than the default `gemma:4b`.

---

## 7. Data Flow Diagram

```
BBRef scraper ──────────────────────────────► nba_panel_raw.csv ──┐
nba_api lineups ────────────────────────────► lineup_raw.csv       │
nba_api on/off ─────────────────────────────► onoff_raw.csv        │
Kaggle CSV ─── ingest_salary.py ────────────► salary_panel.csv     │
                                                                    ▼
                              feature_engineering.py ──► nba_longitudinal_features.csv
                              feature_engineering.py ──► nba_tool_scores.csv
                                                                    │
                              clustering.py ◄────────────────────────┘
                                    │
                                    ├──► nba_archetypes.csv
                                    ├──► reports/cluster_profiles.json
                                    └──► (LLM Layer A for unnamed clusters)
                                                                    │
                              similarity.py ◄──── nba_archetypes.csv
                              similarity.py ◄──── lineup_raw.csv
                              similarity.py ◄──── onoff_raw.csv
                                    │
                                    ├──► player_similarity.csv
                                    └──► lineup_synergy.csv
                                                                    │
                              salary_tiers.py ◄── all above outputs
                                    │
                                    ├──► nba_salary_evaluation.csv
                                    └──► (LLM Layer B → player card narratives)
```

---

## 8. Output Files Reference

| File | Created by | Description |
|---|---|---|
| `data/nba_panel_raw.csv` | `ingest_bbref.py` | Raw per-game + advanced stats, 2019–2025 |
| `data/lineup_raw.csv` | `ingest_nba_api.py` | 2-man lineup net ratings |
| `data/onoff_raw.csv` | `ingest_nba_api.py` | Per-player on/off net ratings |
| `data/salary_panel.csv` | `ingest_salary.py` | Normalized salary data |
| `data/nba_longitudinal_features.csv` | `feature_engineering.py` | Rolling avgs, trajectory, career phase |
| `data/nba_tool_scores.csv` | `feature_engineering.py` | 17 tool scores per player-season |
| `data/nba_archetypes.csv` | `clustering.py` | Cluster assignments + player type labels |
| `reports/cluster_profiles.json` | `clustering.py` | Centroid stats + archetype summaries |
| `data/player_similarity.csv` | `similarity.py` | Top 10 similar player-seasons per player |
| `data/lineup_synergy.csv` | `similarity.py` | Pair-level interaction-effect synergy |
| `data/nba_salary_evaluation.csv` | `salary_tiers.py` | Final ranking, tiers, and verdict |
| `reports/player_cards/*.md` | `salary_tiers.py` (via LLM) | LLM-generated player assessments |
