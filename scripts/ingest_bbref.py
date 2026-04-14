"""
scripts/ingest_bbref.py — Phase 1: Basketball-Reference data ingestion

Pulls per-game and advanced stats for all NBA players across a range of seasons
using the basketball_reference_web_scraper library, then writes a long-format
panel CSV.

Panel key: (bbref_player_id, season)
Season encoding: end-year integer (e.g. 2024-25 season → 2025)
COVID flag: covid_season = True for seasons 2020 and 2021

Rate limit: BBRef enforces ~20 requests/minute. We sleep 3.5 s between season
calls to stay safe. Full 7-season pull takes ~30 seconds.

Usage:
    python scripts/ingest_bbref.py \
        --start-season 2019 \
        --end-season 2025 \
        --out data/nba_panel_raw.csv

Output columns (subset — see plan.md §4-B for full schema):
    player_id, player_name, season, team, age, career_year,
    GP, MPG, PTS, AST, TRB, STL, BLK, TOV,
    TS_pct, eFG_pct, USG_pct, AST_TO_ratio, AST_per36,
    FG3_pct, FG3A_per36, OREB_per36, DREB_per36, BLK_per36, STL_per36,
    PER, BPM, VORP, WS, WS_48, DRTG, DBPM, OREB_pct, DREB_pct,
    AST_pct, TOV_pct, BLK_pct,
    covid_season
"""

import argparse
import time
import pathlib

import pandas as pd

# TODO Phase 1, step 1:
#   from basketball_reference_web_scraper import client as bbref
#   from basketball_reference_web_scraper.data import OutputType

COVID_SEASONS = {2020, 2021}  # end-year integers


def fetch_season_pergame(season_end_year: int) -> pd.DataFrame:
    """Pull per-game stats for one season from BBRef.

    Returns a DataFrame with one row per player-season. Players who were traded
    mid-season appear once per team; keep the 'TOT' row (season total).

    TODO: implement using bbref.players_season_totals(season_end_year=year)
    """
    raise NotImplementedError(
        f"fetch_season_pergame({season_end_year}) not yet implemented. "
        "See plan.md Phase 1."
    )


def fetch_season_advanced(season_end_year: int) -> pd.DataFrame:
    """Pull advanced stats (BPM, VORP, WS, WS/48, DRTG, DBPM, etc.) for one season.

    TODO: implement using bbref.players_season_totals with output_type=ADVANCED
    or a direct HTML scrape of /leagues/NBA_{year}_advanced.html
    """
    raise NotImplementedError(
        f"fetch_season_advanced({season_end_year}) not yet implemented. "
        "See plan.md Phase 1."
    )


def merge_pergame_advanced(pergame: pd.DataFrame, advanced: pd.DataFrame) -> pd.DataFrame:
    """Join per-game and advanced stat DataFrames on (player_id, season, team).

    Drops duplicate stat columns; keeps 'TOT' rows for traded players.

    TODO: implement merge logic
    """
    raise NotImplementedError("merge_pergame_advanced not yet implemented.")


def flag_covid(df: pd.DataFrame) -> pd.DataFrame:
    """Add a boolean covid_season column. True for season end-years 2020 and 2021."""
    df = df.copy()
    df["covid_season"] = df["season"].isin(COVID_SEASONS)
    return df


def build_panel(start: int, end: int) -> pd.DataFrame:
    """Pull and concatenate per-game + advanced stats for seasons start..end (inclusive).

    Respects BBRef rate limit with a 3.5 s sleep between season calls.

    TODO: implement using fetch_season_pergame + fetch_season_advanced + merge
    """
    frames = []
    for year in range(start, end + 1):
        print(f"Fetching season {year - 1}-{str(year)[-2:]}...", flush=True)
        # TODO:
        #   pg = fetch_season_pergame(year)
        #   adv = fetch_season_advanced(year)
        #   merged = merge_pergame_advanced(pg, adv)
        #   frames.append(merged)
        #   time.sleep(3.5)
        raise NotImplementedError(f"Season loop not implemented for year {year}.")

    df = pd.concat(frames, ignore_index=True)
    df = flag_covid(df)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest BBRef stats to panel CSV.")
    parser.add_argument("--start-season", type=int, default=2019,
                        help="First season end-year to pull (default: 2019)")
    parser.add_argument("--end-season", type=int, default=2025,
                        help="Last season end-year to pull (default: 2025)")
    parser.add_argument("--out", type=str, default="data/nba_panel_raw.csv",
                        help="Output CSV path")
    args = parser.parse_args()

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = build_panel(args.start_season, args.end_season)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows → {out_path}")


if __name__ == "__main__":
    main()
