"""
scripts/ingest_salary.py — Phase 1: Salary data ingestion and normalization

Sources:
  - Kaggle NBA Salaries dataset (CSV download, manually placed at data/salaries_raw.csv)
  - Basketball-Reference contracts pages (scrape fallback for missing seasons)

Normalization:
  - pct_league_max = salary_usd / league_max_that_year
    (absolute dollars are non-comparable across seasons due to cap growth)

League max salary history (approximate, update annually):
    2019: $38.2M   2020: $37.1M   2021: $39.3M
    2022: $39.3M   2023: $47.6M   2024: $51.4M   2025: $55.0M

Output: data/salary_panel.csv
    player_id | player_name | season | team | salary_usd |
    pct_league_max | contract_type | covid_season

Joins downstream to nba_panel_raw.csv on (player_id, season).
"""

import pathlib

import pandas as pd

# TODO Phase 1:
#   from basketball_reference_web_scraper import client as bbref

# Approximate league max salary per season end-year.
# Update each summer when the cap is officially set.
LEAGUE_MAX_BY_SEASON: dict[int, float] = {
    2019: 38_200_000,
    2020: 37_100_000,
    2021: 39_300_000,
    2022: 39_300_000,
    2023: 47_600_000,
    2024: 51_400_000,
    2025: 55_000_000,
}


def load_kaggle_salaries(csv_path: str) -> pd.DataFrame:
    """Load the Kaggle NBA salaries CSV and standardize column names.

    Expected input columns (Kaggle format):
        Player, Tm, Season, Salary (negotiable — see TODO)

    TODO: adjust column mapping to match the actual Kaggle dataset schema.
    """
    raise NotImplementedError("load_kaggle_salaries not yet implemented.")


def scrape_bbref_contracts(season_end_year: int) -> pd.DataFrame:
    """Scrape salary data from Basketball-Reference for one season.

    Fallback when Kaggle CSV doesn't cover the season.

    TODO: implement scrape of /leagues/NBA_{year}_contracts.html
    """
    raise NotImplementedError(
        f"scrape_bbref_contracts({season_end_year}) not yet implemented."
    )


def normalize_salaries(df: pd.DataFrame) -> pd.DataFrame:
    """Add pct_league_max column. Requires 'salary_usd' and 'season' columns."""
    df = df.copy()
    df["pct_league_max"] = df.apply(
        lambda r: r["salary_usd"] / LEAGUE_MAX_BY_SEASON.get(r["season"], float("nan")),
        axis=1,
    )
    return df


def main() -> None:
    out_path = pathlib.Path("data/salary_panel.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # TODO:
    #   kaggle_df = load_kaggle_salaries("data/salaries_raw.csv")
    #   # scrape missing seasons if needed
    #   combined = normalize_salaries(combined)
    #   combined.to_csv(out_path, index=False)
    raise NotImplementedError("ingest_salary main() not yet implemented.")


if __name__ == "__main__":
    main()
