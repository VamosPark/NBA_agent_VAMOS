"""
scripts/llm_narrative.py — LLM Layers A + B: Cluster interpretation + Player card narrative

Runtime: Local Ollama endpoint (OpenAI-compatible API).
Default base URL: http://localhost:11434/v1
Default model:    TBD — set LOCAL_MODEL_NAME or $OLLAMA_MODEL env var.

No cloud API keys required.

── Layer A: Cluster Interpretation ─────────────────────────────────────────────

Called by clustering.py for clusters where player_type_similarity < 0.60.

Input (JSON):
    {
      "cluster_id": 3,
      "centroid_tool_scores": {"shooting_ability": 1.8, "handling": -0.4, ...},
      "top_players": ["Player A (2024)", "Player B (2023)", ...]
    }

Output (JSON):
    {
      "archetype_name": "...",
      "description": "...",
      "example_players": ["...", "...", "..."]
    }

── Layer B: Player Card Narrative ───────────────────────────────────────────────

Called by salary_tiers.py after evaluation is complete.

Input (JSON):
    {
      "player": "Draymond Green",
      "archetype": "defensive_anchor",
      "perf_tier": 1,
      "salary_tier": 2,
      "delta": -1,
      "verdict": "UNDERPAID",
      "trajectory_slope": -0.3,
      "consistency_score": 0.82,
      "career_phase": "Prime",
      "top_similar_players": ["Scottie Pippen (2001)", "Ben Wallace (2004)"],
      "best_synergy_partner": "Stephen Curry (interaction_effect: +8.4)"
    }

Output: A 3–4 sentence plain-English player assessment.
"""

import json
import os

LOCAL_MODEL_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LOCAL_MODEL_NAME = os.getenv("OLLAMA_MODEL", "gemma:4b")   # TBD — update when model chosen

# System prompt shared by both layers — kept constant for potential prompt caching.
_SYSTEM_PROMPT = """You are an NBA analytics assistant. You interpret statistical \
cluster data and generate concise, accurate player assessments grounded in \
basketball domain knowledge. Be specific, avoid filler phrases, and flag \
any known limitations of public data (e.g. tracking data not available)."""


def _get_client():
    """Return an OpenAI-compatible client pointed at the local Ollama endpoint.

    TODO: implement using:
        from openai import OpenAI
        return OpenAI(base_url=LOCAL_MODEL_BASE_URL, api_key="ollama")
    """
    raise NotImplementedError("_get_client not yet implemented.")


def interpret_cluster(centroid_stats: dict) -> dict:
    """Layer A — map a K-Means centroid to an archetype name/description.

    Args:
        centroid_stats: dict with keys cluster_id, centroid_tool_scores, top_players

    Returns:
        dict with keys archetype_name, description, example_players

    TODO: implement chat completion call with centroid_stats as user message.
    """
    raise NotImplementedError("interpret_cluster not yet implemented.")


def generate_player_card(player_json: dict) -> str:
    """Layer B — structured player JSON → 3-4 sentence narrative.

    Args:
        player_json: dict matching the Layer B schema described in this module's docstring.

    Returns:
        Plain-text narrative (3-4 sentences).

    TODO: implement chat completion call with player_json serialized as user message.
    """
    raise NotImplementedError("generate_player_card not yet implemented.")


if __name__ == "__main__":
    raise NotImplementedError(
        "Run interpret_cluster() or generate_player_card() from the pipeline scripts, "
        "not directly. See clustering.py and salary_tiers.py."
    )
