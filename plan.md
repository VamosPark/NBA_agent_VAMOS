# NBA Player Performance Analysis — Project Plan
> **Version:** 3.0 (Final)
> **Last Updated:** 2026-04-13
> **Main Target:** Player Performance Analysis (Ranking · Archetype · Synergy)
> **Final Target:** Salary Justification ("Does this player deserve the contract?")
> **Designed for:** Claude Code execution

---

## 0. Project Philosophy

This project is built with two analyst contexts in mind.

**Real-world NBA analyst** has access to Second Spectrum tracking cameras, Synergy
Sports play-by-play tagging, and proprietary internal databases. Their workflow is
top-down: a GM or coach asks a specific question, and the analyst builds a targeted
answer. They never just explore data — every analysis has a decision attached to it.

**Hobby analyst (our context)** starts from aggregate public data — Basketball-Reference,
nba_api, Kaggle. We cannot see where a defender was standing, but we can see the
outcome of every game played since 1996. Our workflow is bottom-up: we find patterns
in what is observable and reason upward toward conclusions.

**Design rule:** We borrow the real-world analyst's *philosophy* (peer group comparison,
role-based evaluation, multi-season trajectory) but execute only what public data
supports. Where tracking data would be needed, we mark it explicitly as a gap — not a
failure, just a known limitation.

**LLM role:** The Python pipeline handles all computation. LLM enters only at the
interpretation and reporting layers, where basketball domain knowledge and natural
language generation add value that code cannot produce.

---

## 1. Context Comparison: Real World vs. Hobby

### 1-A. Data Access

| Data Type | Real World Analyst | Hobby Analyst (Us) |
|---|---|---|
| Traditional box-score stats | ✅ | ✅ Basketball-Reference / nba_api |
| Advanced aggregate stats | ✅ | ✅ BPM, VORP, WS, PER |
| Multi-season historical data | ✅ | ✅ 1996–2025 on BBRef |
| Salary & contract data | ✅ | ✅ Public via BBRef + Kaggle |
| 2-man / 5-man lineup data | ✅ | ✅ nba_api (limited but usable) |
| Optical tracking (x/y/z) | ✅ Second Spectrum | ❌ Proprietary, not public |
| Play-by-play situation tags | ✅ Synergy Sports | ⚠️ Partial (pbpstats.com) |
| Defensive coverage zones | ✅ | ❌ Not available |
| Medical / injury internals | ✅ | ❌ Not available |

### 1-B. Decision Flow Comparison

```
REAL WORLD                          HOBBY (THIS PROJECT)
──────────────────────────────      ──────────────────────────────
GM asks: "Max contract for X?"      Curiosity: "Does X earn his pay?"
         │                                     │
         ▼                                     ▼
Specific question framed            Exploratory analysis
         │                                     │
         ▼                                     ▼
Tracking + Synergy + Box-score      Box-score + Advanced + Lineup
         │                                     │
         ▼                                     ▼
Targeted model for that question    PCA + Clustering + Tier matching
         │                                     │
         ▼                                     ▼
Dashboard → GM presentation         Report + LLM narrative → Insight
         │                                     │
         ▼                                     ▼
Human makes contract decision       Conclusion: Fair / Over / Underpaid
```

### 1-C. What We Can and Cannot Replicate

**We CAN replicate:**
- Peer group (archetype) based comparison — same philosophy, different data source
- Multi-season trajectory analysis — identical method
- On-Off synergy analysis — available via nba_api lineup endpoints
- Within-role ranking — full capability with public advanced stats

**We CANNOT replicate:**
- Shot quality adjusted for defender proximity (needs tracking)
- True defensive impact at play level (needs Synergy tagging)
- Off-ball movement efficiency (needs x/y coordinate data)

**Implication for salary judgment:** Our verdict will be accurate for players whose
value shows up in aggregate stats (scorers, playmakers, traditional bigs). It will
*undervalue* elite defenders like Draymond Green unless we deliberately compensate
via archetype-aware tier assignment.

---

## 2. Analysis Architecture (6 Layers)

### Layer 1 — Longitudinal Profiling

**What:** Build a multi-season profile for each player (2018-19 → 2024-25, 7 seasons).

**Why:** A single season is a snapshot. A contract is a multi-year commitment.
We need to know if a player is ascending, stable, or declining — and how consistent
they are. A player who averages BPM 4.0 every year is a fundamentally different
risk than one who had BPM 4.0 once and oscillates ±3.0.

**Features produced per player:**

| Feature | Formula | Interpretation |
|---|---|---|
| `rolling_avg_3yr` | Mean of last 3 seasons | Smoothed true performance level |
| `trajectory_slope` | Linear slope of WS/48 over seasons | Direction of career arc |
| `consistency_score` | 1 − CV(BPM), where CV = std/mean | Reliability across seasons |
| `career_phase` | Rookie(yr 1-3) / Prime(yr 4-10) / Decline(yr 11+) | Contract risk context |
| `peak_season_bpm` | max(BPM across all seasons) | Ceiling of this player |
| `active_seasons` | Count of seasons with GP ≥ 20 | Durability signal |

**COVID flag:** 2019-20 and 2020-21 seasons had 72 and 72 games. Tag these seasons
with `covid_season = True`. Do not drop them — just normalize stats to per-game and
weight them lower in rolling averages.

**Implementation note:** Use long-format panel data: one row per player per season.
Key: `(player_id, season)`. All downstream layers join on this key.

---

### Layer 2 — Skill-Tool Scoring + PCA + Archetype Clustering

> **See also:** `workflow.plan.md §1–2` for the full skill-tool taxonomy and
> player_type config spec. That document overrides this section where they conflict.

**What:** Compute per-player Tool scores from `configs/tool_mapping.yaml`, then
cluster players into role-based archetypes anchored to `configs/player_types.yaml`.

**Tool taxonomy (summary):** Attack (shooting, handling, passing, off-ball) /
Defense (on-ball, off-ball, disruption) / Rebounding / Intangibles.

**PCA input features** (Tool scores, Z-score normalized):
- Tool scores replace raw stats as clustering inputs.
- PCA is run for interpretability; select components explaining ≥ 80% variance.

**K-Means clustering:** Run k=6 through k=10. Choose k using silhouette score.

**Cluster labeling:** Each centroid is cosine-matched to the closest `player_type`
vector; LLM (local model via Ollama) only names residual clusters below 0.6
similarity threshold.

**Expected archetypes** (names assigned after clustering, not before):

| Archetype | Signature Profile | Example Players |
|---|---|---|
| Elite Two-Way Star | High on all components | LeBron, Giannis |
| Scoring Lead Guard | PC1 + PC2 dominant | Steph Curry, Luka |
| Defensive Anchor | PC3 dominant, low PC1 | Draymond Green, Gobert |
| Playmaking Big | PC2 + PC4, elevated PC1 | Nikola Jokic |
| Stretch / 3&D Wing | PC1 (efficiency), moderate PC3 | Klay Thompson |
| Interior Presence | PC4 dominant | Traditional centers |
| Bench / Role | All components below average | Rotation depth |

---

### Layer 3 — Player Similarity Analysis

**What:** For any player, compute the N most similar players (current or historical).

**Method:** Cosine similarity on PCA component scores.

**Output:** For each player → top 10 most similar players with similarity score.
Include seasons from 2000-01 onward.

---

### Layer 4 — Synergy / Combination Analysis

> **See also:** `workflow.plan.md §3` for the full interaction-effect formula.

**What:** Quantify how specific pairs of players perform *together*.

**Key metric — Interaction Effect:**

```
Synergy(A, B | team) =
    NetRtg_on(A+B on court)
  − NetRtg_off(neither on court)
  − [NetRtg_on(A without B) − NetRtg_off]
  − [NetRtg_on(B without A) − NetRtg_off]
```

Also captures `team_context_tier` (team quality quintile) for context.
Minimum: ≥ 100 shared minutes; falls back to archetype complementarity if < 100.

---

### Layer 5 — Ranking

**Ranking metric (composite):**

```
Rank_score = 0.40 × WS_48_percentile
           + 0.35 × BPM_percentile
           + 0.25 × VORP_percentile
(percentiles computed within archetype group)
```

Two outputs: (1) Absolute league ranking. (2) Within-archetype ranking.

---

### Layer 6 — Salary Justification (Final Layer)

**Performance Tier assignment** (within-archetype percentile):

| Tier | Percentile | Label |
|---|---|---|
| T1 | Top 10% | Franchise-level |
| T2 | 10–30% | All-Star caliber |
| T3 | 30–60% | Solid starter |
| T4 | 60–80% | Rotation player |
| T5 | Bottom 20% | Fringe / bench |

**Salary Tier assignment** (% of league max salary for that contract year):

| Tier | Salary range | Contract type |
|---|---|---|
| T1 | > 85% of max | Supermax / Max |
| T2 | 60–85% of max | Near-max |
| T3 | 35–60% of max | Mid-level range |
| T4 | 15–35% of max | Role player deal |
| T5 | < 15% of max | Minimum / two-way |

**Verdict:**

```
Delta = Salary_Tier − Performance_Tier

Delta ≥ +2  →  SIGNIFICANTLY OVERPAID
Delta = +1  →  OVERPAID
Delta =  0  →  FAIR VALUE
Delta = -1  →  UNDERPAID (bargain)
Delta ≤ -2  →  SIGNIFICANTLY UNDERPAID (hidden asset)
```

---

## 3. LLM Integration

**Runtime:** Local model via Ollama (OpenAI-compatible endpoint at
`http://localhost:11434/v1`). Model TBD (Gemma family).

**Where LLM adds value:**

- **Layer A — Cluster Interpretation:** Name residual clusters that scored < 0.6
  similarity to any player_type. Receives centroid stats JSON, outputs archetype
  name + description.
- **Layer B — Player Card Narrative:** Structured player JSON → 3–4 sentence
  human-readable assessment.
- **Layer C — Conversational Query Interface (optional, Phase 7):** Natural language
  → analysis function call via tool use.

---

## 4. Data Collection Plan

### Datasets

| Dataset | Source | Method | Seasons |
|---|---|---|---|
| Player per-game stats (multi-season) | Basketball-Reference | `basketball_reference_web_scraper` | 2018–2025 |
| Advanced stats (BPM, VORP, WS) | Basketball-Reference | `basketball_reference_web_scraper` | 2018–2025 |
| Player salary per season | Kaggle + BBRef contracts page | CSV + scraper | 2018–2025 |
| 2-man lineup net rating | NBA.com | `nba_api → LeagueDashLineups` | 2021–2025 |
| Career stats (validation) | NBA.com | `nba_api → PlayerCareerStats` | All |

### Schema (long format panel table)

```
player_id | player_name | season | team | age | career_year
| PTS | AST | TRB | STL | BLK | TOV
| TS_pct | eFG_pct | USG_pct | AST_TO
| PER | BPM | VORP | WS | WS_48 | DRTG | DBPM
| GP | MPG
| salary_usd | pct_league_max | contract_type
| covid_season (bool)
```

### Minimum data filter

- `GP >= 20` and `MPG >= 15` applied in `feature_engineering.py`
- Raw panel keeps all rows; flag (do not drop) seasons where `GP < 50`

---

## 5. Phased Work Plan

### Phase 1 — Data Collection & Storage
- Pull per-game + advanced stats (2018–2025) from BBRef
- Pull salary data and join to player records
- Pull 2-man lineup net ratings via nba_api
- Join all data on `(player_id, season)` composite key
- Apply COVID season flags
- Output: `data/nba_panel_raw.csv`

### Phase 2 — Longitudinal Feature Engineering
- Compute rolling 3-season averages
- Compute trajectory slope (linear regression on WS/48 per player)
- Compute consistency score (1 − CV of BPM)
- Assign career phase (Rookie / Prime / Decline)
- Compute Tool scores from `configs/tool_mapping.yaml`
- Output: `data/nba_longitudinal_features.csv`, `data/nba_tool_scores.csv`

### Phase 3 — PCA + Archetype Clustering
- Z-score normalize Tool scores
- Run PCA (≥ 80% variance threshold)
- Run K-Means k=6–10, select by silhouette score
- Label clusters via player_type cosine matching; LLM for residuals
- Output: `data/nba_archetypes.csv`, `reports/cluster_profiles.json`

### Phase 4 — Similarity + Synergy Analysis
- Cosine similarity matrix on PCA scores → top 10 per player
- Compute interaction-effect synergy for pairs with ≥ 100 shared min
- Add team_context_tier
- Output: `data/player_similarity.csv`, `data/lineup_synergy.csv`

### Phase 5 — Ranking + Salary Tier Evaluation
- Within-archetype percentile ranks
- Assign Performance Tier and Salary Tier
- Compute Delta_Tier
- LLM player card narratives
- Output: `data/nba_salary_evaluation.csv`, `reports/player_cards/`

### Phase 6 — Reporting
- Charts: salary vs. performance tier, archetype distribution
- Tables: top 20 overpaid/underpaid, top synergy pairs per team
- Output: `reports/NBA_Performance_Report_2024_25.xlsx`

### Phase 7 — Conversational Interface (Optional)
- Wrap analysis functions as Ollama-compatible tool-use schema
- Register: `query_players()`, `get_player_profile()`, `get_synergy()`,
  `compare_players()`, `get_archetype_ranking()`

---

## 6. Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| pandas | Panel data manipulation |
| scikit-learn | PCA, K-Means, cosine similarity |
| statsmodels | Panel fixed-effects (optional) |
| nba_api | Lineup data + career stats |
| basketball_reference_web_scraper | Advanced multi-season stats |
| matplotlib / seaborn | Visualization |
| openpyxl | Excel output |
| openai (SDK) | Client for local Ollama endpoint |
| PyYAML | Load tool_mapping.yaml / player_types.yaml |

---

## 7. Known Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| No tracking data | Cannot measure defensive coverage quality | Archetype-aware tier partially compensates |
| No Synergy Sports tags | Cannot break down by play type | Use lineup on-off as proxy |
| Public salary data may lag | Contract details occasionally missing | Cross-reference BBRef + Spotrac |
| Lineup data thins for rare pairs | Synergy Score unreliable at < 100 min | Archetype complementarity fallback |
| Small N for time-series (7 pts/player) | Cannot use ML/DL time-series models | Rolling avg + slope only |

---

## 8. File Structure

```
NBA_agent_VAMOS/
├── plan.md                          ← this file
├── workflow.plan.md                 ← addendum: tool-layering & synergy refinement
├── README.md
├── requirements.txt
├── .gitignore
├── configs/
│   ├── tool_mapping.yaml
│   └── player_types.yaml
├── data/
│   ├── nba_panel_raw.csv
│   ├── nba_longitudinal_features.csv
│   ├── nba_tool_scores.csv
│   ├── nba_archetypes.csv
│   ├── player_similarity.csv
│   ├── lineup_synergy.csv
│   └── nba_salary_evaluation.csv
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_pca_clustering.ipynb
│   ├── 04_similarity_synergy.ipynb
│   └── 05_salary_evaluation.ipynb
├── scripts/
│   ├── __init__.py
│   ├── ingest_bbref.py
│   ├── ingest_nba_api.py
│   ├── ingest_salary.py
│   ├── feature_engineering.py
│   ├── clustering.py
│   ├── similarity.py
│   ├── salary_tiers.py
│   └── llm_narrative.py
└── reports/
    ├── cluster_profiles.json
    ├── player_cards/
    └── NBA_Performance_Report_2024_25.xlsx
```

---

*Plan v3.0 — Ready for Claude Code execution*
*See `workflow.plan.md` for skill-tool layering and synergy addendum*
