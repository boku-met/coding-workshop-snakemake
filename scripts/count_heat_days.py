from __future__ import annotations

import argparse
import calendar
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"date", "tmax_c"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Count annual heat days.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--threshold", required=True, type=float)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    daily = pd.read_csv(args.input, parse_dates=["date"])

    missing = REQUIRED_COLUMNS.difference(daily.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if daily.empty:
        raise ValueError("No observations found")

    daily["year"] = daily["date"].dt.year
    daily["is_heat_day"] = daily["tmax_c"] >= args.threshold
    annual = (
        daily.groupby("year", as_index=False)
        .agg(
            heat_days=("is_heat_day", "sum"),
            days_observed=("date", "count"),
            first_observation=("date", "min"),
            last_observation=("date", "max"),
        )
        .sort_values("year")
    )

    expected_days = annual["year"].map(
        lambda year: 366 if calendar.isleap(int(year)) else 365
    )
    annual["complete_year"] = annual["days_observed"] == expected_days
    annual["threshold_c"] = args.threshold
    annual["first_observation"] = annual["first_observation"].dt.strftime("%Y-%m-%d")
    annual["last_observation"] = annual["last_observation"].dt.strftime("%Y-%m-%d")

    columns = [
        "year",
        "heat_days",
        "days_observed",
        "first_observation",
        "last_observation",
        "complete_year",
        "threshold_c",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    annual.to_csv(args.output, columns=columns, index=False)


if __name__ == "__main__":
    main()
