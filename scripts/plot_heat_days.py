from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {
    "year",
    "heat_days",
    "complete_year",
    "last_observation",
    "threshold_c",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot annual heat-day counts.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    annual = pd.read_csv(args.input).sort_values("year")

    missing = REQUIRED_COLUMNS.difference(annual.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if annual.empty:
        raise ValueError("No annual counts found")

    threshold = float(annual["threshold_c"].iloc[0])
    incomplete = annual.loc[~annual["complete_year"]]
    latest = annual.iloc[-1]
    latest_date = pd.Timestamp(latest["last_observation"])

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(annual["year"], annual["heat_days"], color="tab:gray", linewidth=1.35)
    ax.scatter(
        incomplete["year"],
        incomplete["heat_days"],
        facecolors="white",
        edgecolors="tab:orange",
        linewidths=1.5,
        s=45,
        zorder=3,
        label="Incomplete coverage",
    )
    ax.scatter(
        [latest["year"]],
        [latest["heat_days"]],
        color="tab:red",
        s=70,
        zorder=4,
        label=f"{int(latest['year'])} year to date",
    )
    ax.annotate(
        f"{int(latest['heat_days'])} days through {latest_date:%d %b}",
        (latest["year"], latest["heat_days"]),
        xytext=(-12, 18),
        textcoords="offset points",
        ha="right",
        color="tab:red",
    )

    ax.set_title(f"Annual heat days at Wien Hohe Warte (Tmax ≥ {threshold:g} °C)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Heat days")
    ax.set_xlim(annual["year"].min() - 2, annual["year"].max() + 2)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="upper left")
    fig.text(0.99, 0.01, "Source: GeoSphere Austria, klima-v2-1d", ha="right", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
