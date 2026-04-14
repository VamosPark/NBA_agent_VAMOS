"""
scripts/clustering.py — Phase 3: PCA + Archetype Clustering

Inputs:
    data/nba_tool_scores.csv        (from feature_engineering.py)
    configs/player_types.yaml       (player_type key_feature vectors)

Outputs:
    data/nba_archetypes.csv         — original rows + cluster_id, player_type_label,
                                      player_type_similarity, llm_named columns
    reports/cluster_profiles.json   — centroid stats + label + example players

Pipeline:
    1. Load Tool scores (tool_* columns).
    2. Z-score normalize across the full player-season pool.
    3. Run PCA; select components at >= 80% cumulative explained variance.
    4. Run K-Means for k = 6..10; choose k by silhouette score.
    5. For each centroid, cosine-match against player_type key_feature vectors.
    6. Assign player_type label if similarity >= LABEL_THRESHOLD; else flag llm_named=True.
    7. Save outputs.

── Constants ───────────────────────────────────────────────────────────────────
"""

import json
import pathlib

import pandas as pd
import yaml

KMIN = 6
KMAX = 10
LABEL_THRESHOLD = 0.60   # below this → cluster goes to LLM for naming
PCA_VARIANCE_TARGET = 0.80

# TODO Phase 3:
#   from sklearn.preprocessing import StandardScaler
#   from sklearn.decomposition import PCA
#   from sklearn.cluster import KMeans
#   from sklearn.metrics import silhouette_score
#   from sklearn.metrics.pairwise import cosine_similarity
#   import numpy as np


def load_tool_scores(path: str = "data/nba_tool_scores.csv") -> pd.DataFrame:
    """Load Tool score matrix. Returns df with tool_* columns + (player_id, season)."""
    raise NotImplementedError("load_tool_scores not yet implemented.")


def load_player_types(path: str = "configs/player_types.yaml") -> list[dict]:
    """Load player type definitions from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)["player_types"]


def run_pca(tool_matrix, variance_target: float = PCA_VARIANCE_TARGET):
    """Fit PCA and return (pca_model, transformed_scores, n_components)."""
    raise NotImplementedError("run_pca not yet implemented.")


def select_best_k(pca_scores, k_range: range) -> tuple[int, object]:
    """Run K-Means for each k; return (best_k, fitted_model) by silhouette score."""
    raise NotImplementedError("select_best_k not yet implemented.")


def build_player_type_vectors(player_types: list[dict], tool_names: list[str]):
    """Build a binary key_feature matrix: rows=player_types, cols=tools.

    Entry is 1 if the tool is a key_feature for that player_type, else 0.
    Returns (matrix, player_type_names).
    """
    raise NotImplementedError("build_player_type_vectors not yet implemented.")


def label_cluster(centroid, player_type_matrix, player_type_names: list[str],
                  threshold: float = LABEL_THRESHOLD) -> tuple[str, float]:
    """Cosine-match one centroid to the closest player_type.

    Returns (label, similarity). Label is 'unnamed' if similarity < threshold.
    """
    raise NotImplementedError("label_cluster not yet implemented.")


def generate_cluster_profiles(df: pd.DataFrame, tool_cols: list[str]) -> list[dict]:
    """Build cluster_profiles.json content: one entry per cluster.

    Each entry: {cluster_id, player_type_label, player_type_similarity,
                 centroid_tool_scores, top_players, llm_named}
    """
    raise NotImplementedError("generate_cluster_profiles not yet implemented.")


def main() -> None:
    pathlib.Path("reports").mkdir(exist_ok=True)
    player_types = load_player_types()

    # TODO: chain pipeline steps and write outputs
    raise NotImplementedError("clustering main() not yet implemented.")


if __name__ == "__main__":
    main()
