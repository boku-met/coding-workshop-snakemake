from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/vienna_hohe_warte_tlmax.csv"
SOURCE_PATH = ROOT / "data/raw/SOURCE.md"
FIGURE_PATH = ROOT / "figures/heat_days_ge_30.png"
SLIDE_FIGURE_PATH = ROOT / "slides/assets/heat_days.png"

API_URL = "https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1d"
START_DATE = date(1991, 4, 1)
STATION_ID = 5904
PARAMETER = "tlmax"
GENERATED_START = "<!-- BEGIN GENERATED DATA SNAPSHOT -->"
GENERATED_END = "<!-- END GENERATED DATA SNAPSHOT -->"
REQUIRED_COLUMNS = {"time", "station", PARAMETER}


@dataclass(frozen=True)
class SnapshotMetadata:
    query_url: str
    requested_end: date
    retrieved_on: date
    first_usable: date
    latest_usable: date
    checksum: str


def build_query_url(requested_end: date) -> str:
    query = urllib.parse.urlencode(
        {
            "parameters": PARAMETER,
            "station_ids": STATION_ID,
            "start": START_DATE.isoformat(),
            "end": requested_end.isoformat(),
            "output_format": "csv",
        }
    )
    return f"{API_URL}?{query}"


def download_url(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def validate_snapshot(data: bytes, requested_end: date) -> tuple[date, date]:
    if requested_end < START_DATE:
        raise ValueError(f"Requested end date must not precede {START_DATE.isoformat()}")

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("GeoSphere response is not UTF-8 CSV") from error

    reader = csv.DictReader(io.StringIO(text))
    columns = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS.difference(columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    usable_dates: list[date] = []
    seen_dates: set[date] = set()
    for row in reader:
        try:
            station = int(row["station"])
        except (TypeError, ValueError) as error:
            raise ValueError("Invalid station identifier in GeoSphere response") from error
        if station != STATION_ID:
            raise ValueError(f"Expected only station {STATION_ID}")

        try:
            observation_date = datetime.fromisoformat(row["time"]).date()
        except (TypeError, ValueError) as error:
            raise ValueError("Invalid observation date in GeoSphere response") from error
        if observation_date in seen_dates:
            raise ValueError("Expected one observation per date")
        seen_dates.add(observation_date)
        if observation_date > requested_end:
            raise ValueError("GeoSphere response extends beyond the requested end date")

        value = row[PARAMETER]
        if value not in (None, ""):
            try:
                float(value)
            except ValueError as error:
                raise ValueError(f"Invalid {PARAMETER} value in GeoSphere response") from error
            usable_dates.append(observation_date)

    if not seen_dates:
        raise ValueError("GeoSphere response contains no observations")
    if min(seen_dates) != START_DATE:
        raise ValueError(
            f"GeoSphere response does not begin on requested date {START_DATE.isoformat()}"
        )
    expected_days = (requested_end - START_DATE).days + 1
    if len(seen_dates) != expected_days:
        raise ValueError("GeoSphere response does not provide continuous daily coverage")
    if not usable_dates:
        raise ValueError(f"GeoSphere response contains no usable {PARAMETER} values")

    return min(usable_dates), max(usable_dates)


def render_generated_record(metadata: SnapshotMetadata) -> str:
    return f"""{GENERATED_START}
- Station: station `{STATION_ID}`, Wien Hohe Warte
- Parameter: `{PARAMETER}`, maximum 2 m air temperature in degrees Celsius
- Requested interval: {START_DATE.isoformat()} through {metadata.requested_end.isoformat()}
- Usable interval: {metadata.first_usable.isoformat()} through {metadata.latest_usable.isoformat()}
- Retrieved: {metadata.retrieved_on.isoformat()}
- SHA-256: `{metadata.checksum}`

Exact request:

```text
{metadata.query_url}
```
{GENERATED_END}"""


def replace_generated_record(source: str, generated_record: str) -> str:
    start = source.find(GENERATED_START)
    end = source.find(GENERATED_END)
    if start < 0 or end < 0 or end < start:
        raise ValueError("SOURCE.md is missing the generated snapshot markers")
    end += len(GENERATED_END)
    return source[:start] + generated_record + source[end:]


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        temporary_path.chmod(mode)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def refresh_snapshot(
    *,
    raw_path: Path,
    source_path: Path,
    requested_end: date,
    retrieved_on: date,
    download: Callable[[str], bytes] = download_url,
) -> SnapshotMetadata:
    query_url = build_query_url(requested_end)
    data = download(query_url)
    first_usable, latest_usable = validate_snapshot(data, requested_end)
    metadata = SnapshotMetadata(
        query_url=query_url,
        requested_end=requested_end,
        retrieved_on=retrieved_on,
        first_usable=first_usable,
        latest_usable=latest_usable,
        checksum=hashlib.sha256(data).hexdigest(),
    )
    updated_source = replace_generated_record(
        source_path.read_text(), render_generated_record(metadata)
    )

    write_atomic(raw_path, data)
    write_atomic(source_path, updated_source.encode())
    return metadata


def parse_args() -> argparse.Namespace:
    yesterday = datetime.now(ZoneInfo("Europe/Vienna")).date() - timedelta(days=1)
    parser = argparse.ArgumentParser(
        description="Refresh the bundled data, workflow figure, and slide deck."
    )
    parser.add_argument(
        "--end",
        type=date.fromisoformat,
        default=yesterday,
        metavar="YYYY-MM-DD",
        help="requested final date (default: yesterday in Europe/Vienna)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    retrieved_on = datetime.now(ZoneInfo("Europe/Vienna")).date()
    metadata = refresh_snapshot(
        raw_path=RAW_PATH,
        source_path=SOURCE_PATH,
        requested_end=args.end,
        retrieved_on=retrieved_on,
    )
    print(
        "Updated GeoSphere snapshot through "
        f"{metadata.latest_usable.isoformat()} ({metadata.checksum[:12]}…)."
    )

    subprocess.run(
        [
            "snakemake",
            "-s",
            "solutions/Snakefile",
            "--cores",
            "1",
            "--forceall",
            str(FIGURE_PATH.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )
    shutil.copy2(FIGURE_PATH, SLIDE_FIGURE_PATH)
    subprocess.run(["npm", "run", "export-slides"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
