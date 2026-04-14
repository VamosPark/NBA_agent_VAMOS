"""
scripts/salary_tiers.py — Phase 5: Ranking + Salary Tier Evaluation

Inputs:
    data/nba_archetypes.csv         (cluster labels + PCA scores)
    data/nba_longitudinal_features.csv  (rolling avgs, trajectory, career phase)
    data/salary_panel.csv           (salary_usd, pct_league_max)
    data/lineup_synergy.csv         (interaction_effect — referenced in report)

Output:
    data/nba_salary_evaluation.csv
        player_id | player_name | season | player_type_label | career_phase
        | rank_score | within_archetype_rank | league_rank
        | perf_tier | salary_tier | delta_tier | verdict

── Ranking metric (from plan.md §2 Layer 5) ────────────────────────────────────

    rank_score = 0.40 × WS_48_pct   (within-archetype percentile)
               + 0.35 × BPM_pct
               + 0.25 × VORP_pct

── Performance Tier assignment (within-archetype percentile) ────────────────────

    T1  top 10%        Franchise-level
    T2  10–30%         All-Star caliber
    T3  30–60%         Solid starter
    T4  60–80%         Rotation player
    T5  bottom 20%     Fringe / bench

── Salary Tier assignment (pct_league_max) ──────────────────────────────────────

    T1  > 0.85         Supermax / Max
    T2  0.60–0.85      Near-max
    T3  0.35–0.60      Mid-level range
    T4  0.15–0.35      Role player deal
    T5  < 0.15         Minimum / two-way

── Verdict (Delta = Salary_Tier − Performance_Tier) ────────────────────────────

    Delta >= +2   SIGNIFICANTLY OVERPAID
    Delta == +1   OVERPAID
    Delta ==  0   FAIR VALUE
    Delta == -1   UNDERPAID (bargain)
    Delta <= -2   SIGNIFICANTLY UNDERPAID (hidden asset)
"""

import pathlib

import pandas as pd

RANK_WEIGHTS = {"WS_48": 0.40, "BPM": 0.35, "VORP": 0.25}

PERF_TIER_THRESHOLDS = [0.90, 0.70, 0.40, 0.20]  # top-N cutoffs for T1–T4
SALARY_TIER_THRESHOLDS = [0.85, 0.60, 0.35, 0.15]

VERDICT_LABELS = {
    2: "SIGNIFICANTLY OVERPAID",
    1: "OVERPAID",
    0: "FAIR VALUE",
    -1: "UNDERPAID",
}
VERDICT_LABELS_MIN2 = "SIGNIFICANTLY UNDERPAID"


def compute_within_archetype_percentiles(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Add {col}_pct columns: percentile rank within each (player_type_label, season) group."""
    raise NotImplementedError("compute_within_archetype_percentiles not yet implemented.")


def compute_rank_score(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rank_score from weighted within-archetype percentiles."""
    raise NotImplementedError("compute_rank_score not yet implemented.")


def assign_perf_tier(rank_score_pct: float) -> int:
    """Map a player's within-archetype rank_score percentile to T1–T5."""
    raise NotImplementedError("assign_perf_tier not yet implemented.")


def assign_salary_tier(pct_league_max: float) -> int:
    """Map pct_league_max to T1–T5."""
    for tier, threshold in enumerate(SALARY_TIER_THRESHOLDS, start=1):
        if pct_league_max >= threshold:
            return tier
    return 5


def compute_verdict(delta: int) -> str:
    """Map Delta = salary_tier − perf_tier to a verdict string."""
    if delta <= -2:
        return VERDICT_LABELS_MIN2
    return VERDICT_LABELS.get(min(delta, 2), VERDICT_LABELS[2])


def main() -> None:
    pathlib.Path("data").mkdir(exist_ok=True)

    # TODO: load all inputs, compute tiers, write data/nba_salary_evaluation.csv
    raise NotImplementedError("salary_tiers main() not yet implemented.")


if __name__ == "__main__":
    main()
