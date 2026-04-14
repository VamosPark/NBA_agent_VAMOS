"""
scripts/feature_engineering.py — Phase 2: Longitudinal features + Tool scores

Inputs:
    data/nba_panel_raw.csv      (from ingest_bbref.py)
    configs/tool_mapping.yaml   (Tool aggregation rules)

Outputs:
    data/nba_longitudinal_features.csv  — rolling averages, trajectory, career phase
    data/nba_tool_scores.csv            — one Tool-score column per tool per player-season

Panel key: (player_id, season) — all operations respect this grouping.

── Phase 2 steps ───────────────────────────────────────────────────────────────

TODO step 1 — Apply minimum sample filter:
    Keep rows where GP >= 20 AND MPG >= 15.
    Flag (do not drop) rows where GP < 50 → column 'injury_flag' = True.

TODO step 2 — Rolling 3-year averages:
    For each player, sorted by season, compute rolling mean over last 3 seasons
    for all numeric stat columns. Store as {col}_rolling3.
    COVID seasons (covid_season=True) are weighted 0.7× in the rolling mean.

TODO step 3 — Trajectory slope:
    For each player, fit a linear regression of WS_48 ~ season (numeric).
    Store slope as 'trajectory_slope'. Use at least 3 valid seasons;
    if fewer, set NaN and flag 'trajectory_reliable' = False.

TODO step 4 — Consistency score:
    consistency_score = 1 - CV(BPM), where CV = std(BPM) / mean(BPM).
    Computed per player across all valid seasons (GP >= 20).
    Clip to [0, 1] — a player with negative mean BPM gets CV capped at 1.

TODO step 5 — Career phase:
    career_year = seasons since NBA debut (year of first row with GP >= 20).
    career_phase:
        Rookie  → career_year <= 3
        Prime   → 4 <= career_year <= 10
        Decline → career_year > 10

TODO step 6 — Peak season BPM:
    peak_season_bpm = max(BPM) across all seasons with GP >= 20.
    Stored as a player-level constant (same value for all seasons per player).

TODO step 7 — Tool scores:
    Load configs/tool_mapping.yaml.
    For each tool:
        a. Z-score normalize each listed stat across the FULL league (all players,
           all seasons in the panel). Store as {stat}_z columns.
        b. Apply aggregation formula (weighted_z or custom).
        c. Store result as tool_{tool_name} column.
    Output the tool score columns + (player_id, season) key to
    data/nba_tool_scores.csv.
"""

import pathlib

import pandas as pd
import yaml

MIN_GP = 20
MIN_MPG = 15
COVID_SEASONS = {2020, 2021}
COVID_WEIGHT = 0.7


def load_panel(path: str = "data/nba_panel_raw.csv") -> pd.DataFrame:
    """Load the raw panel and sort by (player_id, season)."""
    raise NotImplementedError("load_panel not yet implemented.")


def apply_min_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Apply GP >= MIN_GP and MPG >= MIN_MPG. Flag GP < 50 as injury_flag."""
    raise NotImplementedError("apply_min_filter not yet implemented.")


def compute_rolling_averages(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Add {col}_rolling3 columns. COVID seasons weighted at COVID_WEIGHT."""
    raise NotImplementedError("compute_rolling_averages not yet implemented.")


def compute_trajectory_slope(df: pd.DataFrame) -> pd.DataFrame:
    """Add trajectory_slope and trajectory_reliable columns per player."""
    raise NotImplementedError("compute_trajectory_slope not yet implemented.")


def compute_consistency_score(df: pd.DataFrame) -> pd.DataFrame:
    """Add consistency_score per player (1 - CV of BPM)."""
    raise NotImplementedError("compute_consistency_score not yet implemented.")


def assign_career_phase(df: pd.DataFrame) -> pd.DataFrame:
    """Add career_year and career_phase columns."""
    raise NotImplementedError("assign_career_phase not yet implemented.")


def compute_peak_bpm(df: pd.DataFrame) -> pd.DataFrame:
    """Add peak_season_bpm column (player-level constant)."""
    raise NotImplementedError("compute_peak_bpm not yet implemented.")


def compute_tool_scores(df: pd.DataFrame, tool_mapping: dict) -> pd.DataFrame:
    """Compute z-scores for each stat and aggregate into Tool score columns.

    Returns a DataFrame with (player_id, season) + tool_* columns.
    """
    raise NotImplementedError("compute_tool_scores not yet implemented.")


def main() -> None:
    tool_mapping_path = pathlib.Path("configs/tool_mapping.yaml")
    with open(tool_mapping_path) as f:
        tool_mapping = yaml.safe_load(f)

    # TODO: chain the pipeline steps and write outputs
    raise NotImplementedError("feature_engineering main() not yet implemented.")


if __name__ == "__main__":
    main()
