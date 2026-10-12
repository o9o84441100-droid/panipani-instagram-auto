"""Sanity checks for missing-slot audit without posting."""
import tempfile
import unittest
from datetime import date
from pathlib import Path
from audit_previous_day import audit, SLOTS


class DailyAuditTest(unittest.TestCase):
    def test_before_launch_has_no_alerts(self):
        with tempfile.TemporaryDirectory() as t:
            day, missing = audit(date(2026, 10, 12), Path(t))
            self.assertEqual(missing, [])

    def test_detects_only_unrecorded_slots(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "2026-10-13_0800.json").write_text("{}", encoding="utf-8")
            (root / "2026-10-13_1200.json").write_text("{}", encoding="utf-8")
            _, missing = audit(date(2026, 10, 13), root)
            self.assertEqual(missing, ["1000", "1800", "2100"])

    def test_complete_day_is_clear(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for slot in SLOTS:
                (root / ("2026-10-13_" + slot + ".json")).write_text("{}", encoding="utf-8")
            _, missing = audit(date(2026, 10, 13), root)
            self.assertFalse(missing)

if __name__ == "__main__":
    unittest.main()
