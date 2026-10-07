from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.refresh_workshop import refresh_snapshot


VALID_CSV = b"""time,station,tlmax
1991-04-01T00:00+00:00,5904,10.0
1991-04-02T00:00+00:00,5904,31.0
1991-04-03T00:00+00:00,5904,
"""

SOURCE_TEMPLATE = """# Source record

Before the generated record.

<!-- BEGIN GENERATED DATA SNAPSHOT -->
old metadata
<!-- END GENERATED DATA SNAPSHOT -->

After the generated record.
"""


class RefreshSnapshotTests(unittest.TestCase):
    def test_valid_response_replaces_snapshot_and_generated_source_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "observations.csv"
            source_path = root / "SOURCE.md"
            raw_path.write_text("old csv\n")
            source_path.write_text(SOURCE_TEMPLATE)

            metadata = refresh_snapshot(
                raw_path=raw_path,
                source_path=source_path,
                requested_end=date(1991, 4, 3),
                retrieved_on=date(1991, 4, 4),
                download=lambda _url: VALID_CSV,
            )

            self.assertEqual(raw_path.read_bytes(), VALID_CSV)
            self.assertEqual(raw_path.stat().st_mode & 0o777, 0o644)
            self.assertEqual(source_path.stat().st_mode & 0o777, 0o644)
            source = source_path.read_text()
            self.assertIn("1991-04-01 through 1991-04-03", source)
            self.assertIn("1991-04-01 through 1991-04-02", source)
            self.assertIn("Retrieved: 1991-04-04", source)
            self.assertIn(
                "SHA-256: `f79e184ebefde4dda846cb9307041bfa09237aba7138f5c45e6b1eb7a19ff851`",
                source,
            )
            self.assertIn("After the generated record.", source)
            self.assertEqual(metadata.latest_usable, date(1991, 4, 2))

    def test_invalid_response_leaves_existing_snapshot_and_source_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "observations.csv"
            source_path = root / "SOURCE.md"
            raw_path.write_text("old csv\n")
            source_path.write_text(SOURCE_TEMPLATE)
            original_raw = raw_path.read_bytes()
            original_source = source_path.read_text()
            wrong_station = VALID_CSV.replace(b",5904,", b",105,")

            with self.assertRaisesRegex(ValueError, "station 5904"):
                refresh_snapshot(
                    raw_path=raw_path,
                    source_path=source_path,
                    requested_end=date(1991, 4, 3),
                    retrieved_on=date(1991, 4, 4),
                    download=lambda _url: wrong_station,
                )

            self.assertEqual(raw_path.read_bytes(), original_raw)
            self.assertEqual(source_path.read_text(), original_source)

    def test_truncated_response_leaves_existing_snapshot_and_source_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "observations.csv"
            source_path = root / "SOURCE.md"
            raw_path.write_text("old csv\n")
            source_path.write_text(SOURCE_TEMPLATE)
            original_raw = raw_path.read_bytes()
            original_source = source_path.read_text()
            truncated = VALID_CSV.replace(
                b"1991-04-01T00:00+00:00,5904,10.0\n", b""
            )

            with self.assertRaisesRegex(ValueError, "1991-04-01"):
                refresh_snapshot(
                    raw_path=raw_path,
                    source_path=source_path,
                    requested_end=date(1991, 4, 3),
                    retrieved_on=date(1991, 4, 4),
                    download=lambda _url: truncated,
                )

            self.assertEqual(raw_path.read_bytes(), original_raw)
            self.assertEqual(source_path.read_text(), original_source)

    def test_response_with_internal_date_gap_leaves_snapshot_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "observations.csv"
            source_path = root / "SOURCE.md"
            raw_path.write_text("old csv\n")
            source_path.write_text(SOURCE_TEMPLATE)
            original_raw = raw_path.read_bytes()
            original_source = source_path.read_text()
            gap = VALID_CSV.replace(
                b"1991-04-02T00:00+00:00,5904,31.0\n", b""
            )

            with self.assertRaisesRegex(ValueError, "daily coverage"):
                refresh_snapshot(
                    raw_path=raw_path,
                    source_path=source_path,
                    requested_end=date(1991, 4, 3),
                    retrieved_on=date(1991, 4, 4),
                    download=lambda _url: gap,
                )

            self.assertEqual(raw_path.read_bytes(), original_raw)
            self.assertEqual(source_path.read_text(), original_source)


if __name__ == "__main__":
    unittest.main()
