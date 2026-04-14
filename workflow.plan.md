# Workflow Plan Addendum — Skill-Tool Layering & Synergy Refinement

> **Companion to:** `plan.md` (v3.0)
> **Purpose:** Refine three execution details that the v3.0 plan left
> under-specified. This document overrides the matching sections of
> `plan.md` where they conflict.

---

## 1. Skill-Tool Layering (new feature-engineering concept)

The term "Tool" here means a player *ability* in the sports-scouting sense
— the specific skills that make a player useful. Players are not atomic;
they are a bundle of tools, and clustering should operate on the tool
bundle, not on raw box-score columns.

### 1-A. Tool taxonomy (3 layers)

```
Layer 0 — Phase          Layer 1 — Skill Group    Layer 2 — Tool (measurable)
────────────────────     ──────────────────────   ─────────────────────────────
Attack                   Scoring                   Shooting ability
                                                   Finishing at rim
                                                   Mid-range efficiency
                         Creation                  Handling
                                                   Passing / vision
                                                   Pick-and-roll navigation
                         Off-ball                  Spot-up shooting
                                                   Cutting
Defense                  On-ball defense           Perimeter containment
                                                   Post defense
                         Off-ball defense          Help rotation
                                                   Rim protection
                         Disruption                Steals
                                                   Shot-blocking
Rebounding               Offensive glass           OREB%
                         Defensive glass           DREB%
Intangibles              Efficiency                TS%, eFG%
                         Durability                GP, MPG
                         Usage discipline          TOV%, AST/TO
```

Each Tool is computed from one or more public stats — this mapping lives in
a single config file so the taxonomy is data, not code.

### 1-B. Config file — `configs/tool_mapping.yaml`

```yaml
tools:
  shooting_ability:
    phase: attack
    skill_group: scoring
    stats: [TS_pct, eFG_pct, FG3_pct, FT_pct]
    aggregation: weighted_z   # z-score each stat, weighted mean
    weights: [0.35, 0.25, 0.30, 0.10]

  handling:
    phase: attack
    skill_group: creation
    stats: [AST_pct, TOV_pct, USG_pct]
    aggregation: custom       # AST% up, TOV% down, USG% context
    formula: "AST_pct_z - 0.8*TOV_pct_z + 0.2*USG_pct_z"

  passing_vision:
    phase: attack
    skill_group: creation
    stats: [AST_per36, AST_TO_ratio, AST_pct]
    aggregation: weighted_z
    weights: [0.4, 0.3, 0.3]

  rim_protection:
    phase: defense
    skill_group: off_ball
    stats: [BLK_per36, BLK_pct, DRTG, DBPM]
    aggregation: weighted_z
    weights: [0.25, 0.35, -0.2, 0.2]   # DRTG inverted (lower=better)

  # ...continues for every Tool
```

### 1-C. Player-type → key-features mapping

Second config — defines hypothesized archetypes and which Tools
define them. This is the `{"player_type": ..., "key_features": [...]}`
structure requested in the user's addendum.

`configs/player_types.yaml`:

```yaml
player_types:
  - player_type: shooter
    key_features:
      - shooting_ability
      - spot_up_shooting
      - off_ball_cutting
    anti_features:      # low weight on these = still a shooter
      - handling
      - post_defense

  - player_type: primary_creator
    key_features:
      - handling
      - passing_vision
      - pick_and_roll
      - shooting_ability

  - player_type: defensive_anchor
    key_features:
      - rim_protection
      - help_rotation
      - perimeter_containment
      - dreb_pct

  - player_type: two_way_wing
    key_features:
      - shooting_ability
      - perimeter_containment
      - cutting
      - disruption

  - player_type: playmaking_big
    key_features:
      - passing_vision
      - post_scoring
      - oreb_pct
      - rim_protection

  - player_type: rebounding_big
    key_features:
      - oreb_pct
      - dreb_pct
      - rim_protection
      - finishing_at_rim

  - player_type: role_connector
    key_features:
      - efficiency
      - usage_discipline
      - spot_up_shooting
      - help_rotation
```

### 1-D. Impact on `scripts/feature_engineering.py`

The script gets a new stage **between** the longitudinal rolling averages
and the clustering step:

```
raw panel
  → rolling 3-yr averages (existing)
  → per-stat Z-score normalization (existing)
  → [NEW] Tool scores: aggregate stats into Tool columns per tool_mapping.yaml
  → [NEW] player_type candidate scores: for each type, mean(Tool_z over key_features)
  → output: data/nba_tool_scores.csv (one row per player-season,
            columns = 1 per Tool + 1 per player_type candidate score)
```

This file becomes the **input to clustering**, replacing the "raw advanced
stats" feature matrix described in §2 Layer 2 of `plan.md`.

---

## 2. Clustering driven by key_features (override of plan.md §2 Layer 2)

**Previous v3.0 approach:** PCA on ~20 raw advanced stats → K-Means on
PCA components → LLM names the clusters.

**Revised approach:**

1. Compute all Tool scores from `tool_mapping.yaml`.
2. Build the feature matrix as **one column per Tool** (not raw stats). This
   is a ~15-dimensional Tool-space, already de-collinearized by design.
3. Run PCA on Tool-space for interpretability only (optional — can skip if
   Tool columns are already roughly orthogonal; verify with a correlation
   heatmap).
4. Run K-Means (k=6–10, select by silhouette) on Tool scores directly.
5. For each resulting cluster centroid, compute its cosine similarity
   against each `player_type` key-feature vector from `player_types.yaml`.
6. **Assign the cluster the label of the closest player_type.** If the top
   similarity is below a threshold (e.g. 0.6), flag the cluster as
   `unnamed_N` and surface it to the LLM for naming (Layer A fallback).

**Why this matters:** clusters are now anchored to basketball-domain
archetypes before the LLM sees them. The LLM interprets *residual* clusters,
not every cluster. This reduces hallucination risk and makes the archetypes
reproducible across seasons.

### Impact on `scripts/clustering.py`

New functions:

```python
def compute_tool_scores(panel_df, tool_mapping) -> pd.DataFrame: ...
def score_player_type_fit(tool_scores, player_types) -> pd.DataFrame: ...
def label_cluster_by_player_type(centroid, player_types, threshold=0.6) -> str: ...
```

Output columns added to `data/nba_archetypes.csv`:
- `cluster_id` (K-Means label)
- `player_type_label` (matched from config)
- `player_type_similarity` (cosine sim to closest type vector)
- `llm_named` (bool — True only if match was below threshold)

---

## 3. Synergy refinement — team quality + 2-player +/- margin (override of plan.md §2 Layer 4)

**Previous v3.0 approach:** Synergy(A,B) = NetRtg(A+B) − mean(NetRtg(A solo), NetRtg(B solo)).

**Problem with it:** a pair on a great team looks synergistic just because
the team around them is strong. A pair on a bad team looks anti-synergistic
even if they personally click. We need to separate pair-specific effect from
team-level baseline.

### 3-A. Revised synergy formula

```
Synergy(A, B | team) =
    NetRtg_on(A+B on court)
  − NetRtg_off(neither A nor B on court, same team, same season)
  − [ NetRtg_on(A without B) − NetRtg_off ]
  − [ NetRtg_on(B without A) − NetRtg_off ]
```

Reading:
- First term = raw impact when both are on.
- Second/third terms = each player's *solo* lift over team baseline.
- Subtracting them leaves the **interaction effect** — the part of the
  lineup's performance that neither player produces alone.

This is mathematically equivalent to a 2-way interaction term in a linear
on/off regression, but computable directly from lineup data without fitting
a model.

### 3-B. Team-quality context column

Each player-season also gets:

- `team_baseline_netrtg` — team NetRtg with this player off the court.
- `team_context_tier` — quintile of team_baseline_netrtg across the league
  that season (T1 = top 20% team, T5 = bottom 20%).

**Purpose:** when reporting synergy, show it alongside team tier so readers
can distinguish "made a great team even better" from "kept a bad team afloat".

### 3-C. Minimum-sample rule (unchanged, restated)

- Require ≥ 100 shared minutes between A and B in the season.
- Require ≥ 100 solo minutes for each of A-without-B and B-without-A.
- If either solo sample is < 100 min (e.g. tandem always plays together),
  fall back to the **archetype complementarity proxy** from plan.md §2
  Layer 4 and flag the pair as `synergy_proxy = True`.

### 3-D. Impact on `scripts/similarity.py`

Renamed/extended:

```python
def compute_pair_synergy(
    lineup_df,          # nba_api LeagueDashLineups
    team_onoff_df,      # nba_api TeamPlayerOnOffDetails
    min_shared_min: int = 100,
) -> pd.DataFrame: ...
# returns columns: player_a, player_b, team, season, shared_min,
#                  netrtg_pair, interaction_effect, team_baseline_netrtg,
#                  team_context_tier, synergy_proxy (bool)
```

New data file: `data/lineup_synergy.csv` gains the columns above. Salary
tier report (Phase 5) references `interaction_effect` — not raw pair
NetRtg — when judging whether two expensive contracts "work together".

---

## 4. Files touched / added

| File | Status | Purpose |
|---|---|---|
| `configs/tool_mapping.yaml` | **NEW** | Stat → Tool aggregation rules |
| `configs/player_types.yaml` | **NEW** | player_type → key_features |
| `scripts/feature_engineering.py` | extended | Tool-score computation stage |
| `scripts/clustering.py` | extended | Cluster → player_type label assignment |
| `scripts/similarity.py` | extended | Interaction-effect synergy formula |
| `data/nba_tool_scores.csv` | **NEW** | Tool-space feature matrix |
| `data/nba_archetypes.csv` | extended | `player_type_label`, `llm_named` cols |
| `data/lineup_synergy.csv` | extended | `interaction_effect`, `team_context_tier` cols |

---

## 5. Open questions to resolve before implementation

1. **Tool weight tuning** — the weights in `tool_mapping.yaml` are domain
   guesses. Should we validate them against a ground-truth set of
   well-known archetypes (e.g. "does Curry score high on `shooting_ability`
   tool?") before committing them? Suggest a unit-test style
   `tests/test_tool_mapping.py` that asserts known players land in expected
   player_types.

2. **player_type overlap** — a player like LeBron scores high on both
   `primary_creator` and `two_way_wing`. Do we:
   - (a) pick the single best match (hard label), or
   - (b) return a soft distribution over all player_types (e.g.
         `{"primary_creator": 0.55, "two_way_wing": 0.40, ...}`)?
   Soft labels are more honest but harder to display. Default proposal: (b)
   in the data, (a) in the report.

3. **Synergy denominator** — should `interaction_effect` be normalized by
   shared minutes (per-100 possessions already does this) or by team pace?
   Default: stick with per-100-possessions convention, same as NBA.com.

---

*Plan addendum v1 — authored 2026-04-14*
