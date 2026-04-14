"""
scripts/similarity.py — Phase 4: Player similarity + Synergy analysis

Inputs:
    data/nba_archetypes.csv     (PCA component scores from clustering.py)
    data/lineup_raw.csv         (2-man lineup net ratings from ingest_nba_api.py)
    data/onoff_raw.csv          (per-player on/off net ratings from ingest_nba_api.py)
    configs/player_types.yaml   (for archetype complementarity fallback)

Outputs:
    data/player_similarity.csv
        player_id | season | similar_rank | similar_player_id | similar_player_name
        | similarity_score | is_historical

    data/lineup_synergy.csv
        player_a | player_b | team | season | shared_min
        | netrtg_pair | interaction_effect | team_baseline_netrtg
        | team_context_tier | synergy_proxy (bool)

── Synergy formula (from workflow.plan.md §3) ──────────────────────────────────

    interaction_effect(A, B | team) =
        NetRtg_on(A+B on court)
      − NetRtg_off(neither A nor B on court)      ← team baseline
      − [NetRtg_on(A without B) − NetRtg_off]     ← A's solo lift
      − [NetRtg_on(B without A) − NetRtg_off]     ← B's solo lift

    Positive → A and B make each other better than solo contributions
    Near 0   → independent contributors
    Negative → conflict (usage overlap, defensive mismatch, etc.)

── Minimum-sample rules ────────────────────────────────────────────────────────
    Require >= 100 shared minutes for pair-level NetRtg.
    Require >= 100 solo minutes for each of A-without-B and B-without-A.
    If either solo sample is < 100 min → use archetype complementarity proxy
    and set synergy_proxy = True.
"""

import pathlib

import pandas as pd
import yaml

MIN_SHARED_MIN = 100
MIN_SOLO_MIN = 100
TOP_N_SIMILAR = 10   # similar players to return per player-season

# TODO Phase 4:
#   from sklearn.metrics.pairwise import cosine_similarity
#   import numpy as np


def load_pca_scores(path: str = "data/nba_archetypes.csv") -> pd.DataFrame:
    """Load PCA component score columns. Returns df with (player_id, season) + pc_* cols."""
    raise NotImplementedError("load_pca_scores not yet implemented.")


def compute_similarity_matrix(pca_scores) -> "np.ndarray":
    """Cosine similarity on PCA component scores. Returns (N x N) matrix."""
    raise NotImplementedError("compute_similarity_matrix not yet implemented.")


def extract_top_n_similar(similarity_matrix, df: pd.DataFrame,
                           n: int = TOP_N_SIMILAR) -> pd.DataFrame:
    """For each player-season, return top N most similar other player-seasons.

    Include historical (pre-current-season) entries so we can say
    'profiles like peak Scottie Pippen'.
    """
    raise NotImplementedError("extract_top_n_similar not yet implemented.")


def compute_team_baseline(onoff_df: pd.DataFrame) -> pd.DataFrame:
    """Compute team NetRtg with target player OFF the court (team baseline).

    Returns df with (team, season, player_id, team_baseline_netrtg).
    """
    raise NotImplementedError("compute_team_baseline not yet implemented.")


def compute_interaction_effect(
    lineup_df: pd.DataFrame,
    onoff_df: pd.DataFrame,
    min_shared: int = MIN_SHARED_MIN,
    min_solo: int = MIN_SOLO_MIN,
) -> pd.DataFrame:
    """Apply the interaction-effect synergy formula to all qualifying pairs.

    For pairs below min_solo threshold → synergy_proxy = True (fallback handled
    separately in assign_archetype_complementarity).
    """
    raise NotImplementedError("compute_interaction_effect not yet implemented.")


def assign_archetype_complementarity(
    pairs_df: pd.DataFrame,
    archetypes_df: pd.DataFrame,
    player_types: list[dict],
) -> pd.DataFrame:
    """Fallback synergy proxy for pairs with insufficient solo minutes.

    Two players are complementary if their player_type key_features have
    low overlap (cosine similarity of key_feature vectors < 0.40).
    Sets interaction_effect = NaN and synergy_proxy = True.
    """
    raise NotImplementedError("assign_archetype_complementarity not yet implemented.")


def assign_team_context_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Classify team_baseline_netrtg into quintile tiers (T1=top 20%, T5=bottom 20%)
    relative to all teams in the same season."""
    raise NotImplementedError("assign_team_context_tier not yet implemented.")


def main() -> None:
    pathlib.Path("data").mkdir(exist_ok=True)
    with open("configs/player_types.yaml") as f:
        player_types = yaml.safe_load(f)["player_types"]

    # TODO: chain pipeline steps and write outputs
    raise NotImplementedError("similarity main() not yet implemented.")


if __name__ == "__main__":
    main()
