"""
scripts/ingest_nba_api.py — Phase 1 + Phase 4: NBA.com data ingestion

Pulls two datasets via nba_api:
  1. PlayerCareerStats  — career game totals for player ID validation (Phase 1)
  2. LeagueDashLineups  — 2-man and 5-man lineup net ratings (Phase 4)
  3. TeamPlayerOnOffDetails — per-player on/off net rating for synergy formula

nba_api rate limit: unofficial, ~5 req/s is safe. Add a 0.6 s sleep between calls.

Usage:
    python scripts/ingest_nba_api.py --seasons 2022 2023 2024 2025 \
        --out-lineups data/lineup_raw.csv \
        --out-onoff   data/onoff_raw.csv

Output files:
    lineup_raw.csv   — 2-man combo stats: player_a, player_b, team, season,
                       shared_min, off_rtg, def_rtg, net_rtg
    onoff_raw.csv    — player on/off: player_id, team, season,
                       on_net_rtg, off_net_rtg, on_min, off_min
"""

import argparse
import time
import pathlib

import pandas as pd

# TODO Phase 1/4:
#   from nba_api.stats.endpoints import (
#       LeagueDashLineups,
#       PlayerCareerStats,
#       TeamPlayerOnOffDetails,
#   )

NBA_API_SLEEP = 0.6  # seconds between API calls


def fetch_lineup_data(season_str: str) -> pd.DataFrame:
    """Pull 2-man lineup net ratings for a season via LeagueDashLineups.

    season_str format: "2024-25"

    TODO: implement using LeagueDashLineups(
        season=season_str,
        measure_type_grouping="Advanced",
        group_quantity=2,
        ...
    )
    """
    raise NotImplementedError(
        f"fetch_lineup_data({season_str!r}) not yet implemented. See plan.md Phase 4."
    )


def fetch_onoff_data(team_id: int, season_str: str) -> pd.DataFrame:
    """Pull per-player on/off net rating for a team via TeamPlayerOnOffDetails.

    Required for the interaction-effect synergy formula in workflow.plan.md §3.

    TODO: implement using TeamPlayerOnOffDetails(
        team_id=team_id,
        season=season_str,
        ...
    )
    """
    raise NotImplementedError(
        f"fetch_onoff_data(team_id={team_id}, season={season_str!r}) not yet implemented."
    )


def season_end_year_to_str(year: int) -> str:
    """Convert end-year integer to NBA season string. 2025 → '2024-25'."""
    return f"{year - 1}-{str(year)[-2:]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest nba_api lineup + on/off data.")
    parser.add_argument("--seasons", type=int, nargs="+", default=[2022, 2023, 2024, 2025],
                        help="Season end-years to pull")
    parser.add_argument("--out-lineups", type=str, default="data/lineup_raw.csv")
    parser.add_argument("--out-onoff", type=str, default="data/onoff_raw.csv")
    args = parser.parse_args()

    for path in [args.out_lineups, args.out_onoff]:
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

    lineup_frames = []
    onoff_frames = []
    for year in args.seasons:
        season_str = season_end_year_to_str(year)
        print(f"Fetching lineups for {season_str}...", flush=True)
        # TODO:
        #   lineup_frames.append(fetch_lineup_data(season_str))
        #   time.sleep(NBA_API_SLEEP)
        #   ... fetch on/off per team ...
        raise NotImplementedError(f"Season loop not implemented for {season_str}.")

    pd.concat(lineup_frames, ignore_index=True).to_csv(args.out_lineups, index=False)
    pd.concat(onoff_frames, ignore_index=True).to_csv(args.out_onoff, index=False)


if __name__ == "__main__":
    main()
