from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"time", "station", "tlmax"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the bundled GeoSphere data.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw = pd.read_csv(args.input)

    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    dates = pd.to_datetime(raw["time"], utc=True, errors="raise")
    temperatures = pd.to_numeric(raw["tlmax"], errors="coerce")
    clean = pd.DataFrame(
        {
            "date": dates.dt.strftime("%Y-%m-%d"),
            "tmax_c": temperatures,
        }
    ).dropna(subset=["tmax_c"])

    if clean["date"].duplicated().any():
        raise ValueError("Expected one observation per date")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
