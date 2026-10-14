"""No-publication validation for daily Panipani workflow."""
import os
import unittest
from datetime import date
from pathlib import Path

import daily_reel
from daily_topics import TOPICS

class DailyReelTest(unittest.TestCase):
    def test_topics(self):
        self.assertGreaterEqual(len(TOPICS), 80)
        for title, use_case, prompt, caution in TOPICS:
            self.assertTrue(title and use_case and prompt and caution)
            self.assertLessEqual(len(prompt), 130)

    def test_schedule_coverage(self):
        self.assertEqual(set(daily_reel.CRON_TO_SLOT.values()), set(daily_reel.SLOTS))
        old_event = os.environ.get("GITHUB_EVENT_NAME")
        old_schedule = os.environ.get("GITHUB_EVENT_SCHEDULE")
        try:
            os.environ["GITHUB_EVENT_NAME"] = "schedule"
            for expr, slot in daily_reel.CRON_TO_SLOT.items():
                os.environ["GITHUB_EVENT_SCHEDULE"] = expr
                from datetime import datetime
                from unittest.mock import patch
                from zoneinfo import ZoneInfo
                with patch.object(daily_reel, "datetime", wraps=datetime) as clock:
                    clock.now.return_value = datetime(2026, 10, 14, int(slot[:2]), 5, tzinfo=ZoneInfo("Asia/Tokyo"))
                    self.assertEqual(daily_reel.context()["slot"], slot)
        finally:
            if old_event is None: os.environ.pop("GITHUB_EVENT_NAME", None)
            else: os.environ["GITHUB_EVENT_NAME"] = old_event
            if old_schedule is None: os.environ.pop("GITHUB_EVENT_SCHEDULE", None)
            else: os.environ["GITHUB_EVENT_SCHEDULE"] = old_schedule

    def test_manual_slot_validation(self):
        old_event = os.environ.get("GITHUB_EVENT_NAME")
        old_slot = os.environ.get("MANUAL_SLOT")
        try:
            os.environ["GITHUB_EVENT_NAME"] = "workflow_dispatch"
            os.environ["MANUAL_SLOT"] = "garbage"
            with self.assertRaises(RuntimeError):
                daily_reel.context()
        finally:
            if old_event is None: os.environ.pop("GITHUB_EVENT_NAME", None)
            else: os.environ["GITHUB_EVENT_NAME"] = old_event
            if old_slot is None: os.environ.pop("MANUAL_SLOT", None)
            else: os.environ["MANUAL_SLOT"] = old_slot

    def test_github_output_is_only_key_value_lines(self):
        import io
        from contextlib import redirect_stdout
        old_event = os.environ.get("GITHUB_EVENT_NAME")
        old_slot = os.environ.get("MANUAL_SLOT")
        try:
            os.environ["GITHUB_EVENT_NAME"] = "workflow_dispatch"
            os.environ["MANUAL_SLOT"] = "0800"
            stream = io.StringIO()
            with redirect_stdout(stream):
                daily_reel.guard()
            lines = stream.getvalue().splitlines()
            self.assertTrue(any(x.startswith("slot_key=") for x in lines))
            self.assertTrue(any(x.startswith("should_publish=") for x in lines))
            self.assertTrue(all("=" in x for x in lines))
        finally:
            if old_event is None: os.environ.pop("GITHUB_EVENT_NAME", None)
            else: os.environ["GITHUB_EVENT_NAME"] = old_event
            if old_slot is None: os.environ.pop("MANUAL_SLOT", None)
            else: os.environ["MANUAL_SLOT"] = old_slot

    def test_different_slots_have_different_topics(self):
        old_event = os.environ.get("GITHUB_EVENT_NAME")
        old_slot = os.environ.get("MANUAL_SLOT")
        try:
            os.environ["GITHUB_EVENT_NAME"] = "workflow_dispatch"
            selected = set()
            for slot in daily_reel.SLOTS:
                os.environ["MANUAL_SLOT"] = slot
                info = daily_reel.context()
                selected.add(info["topic"][0])
                self.assertIn(info["slot"], daily_reel.SLOTS)
            self.assertEqual(len(selected), 5)
        finally:
            if old_event is None: os.environ.pop("GITHUB_EVENT_NAME", None)
            else: os.environ["GITHUB_EVENT_NAME"] = old_event
            if old_slot is None: os.environ.pop("MANUAL_SLOT", None)
            else: os.environ["MANUAL_SLOT"] = old_slot


class ScheduleSafetyTests(unittest.TestCase):
    def test_time_window_blocks_cron_run_for_wrong_jst_hour(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from unittest.mock import patch
        info = {"day": "2026-10-13", "slot": "1800"}
        tz = ZoneInfo("Asia/Tokyo")
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule"}):
            self.assertTrue(daily_reel.scheduled_window_is_valid(info, datetime(2026, 10, 13, 18, 5, tzinfo=tz)))
            self.assertTrue(daily_reel.scheduled_window_is_valid(info, datetime(2026, 10, 13, 20, 5, tzinfo=tz)))
            self.assertFalse(daily_reel.scheduled_window_is_valid(info, datetime(2026, 10, 13, 18, 4, tzinfo=tz)))
            self.assertFalse(daily_reel.scheduled_window_is_valid(info, datetime(2026, 10, 13, 20, 6, tzinfo=tz)))
            self.assertFalse(daily_reel.scheduled_window_is_valid(info, datetime(2026, 10, 14, 18, 5, tzinfo=tz)))

    def test_paused_switch_prevents_publication_even_without_ledger(self):
        from io import StringIO
        from contextlib import redirect_stdout
        from unittest.mock import patch
        info = {"day": "2026-10-14", "slot": "1800", "key": "2026-10-14_1800"}
        with (patch.dict(os.environ, {"GITHUB_EVENT_NAME":"workflow_dispatch", "PANIPANI_PUBLICATION_ENABLED":"false"}),
              patch.object(daily_reel, "context", return_value=info),
              patch.object(daily_reel, "state_file", return_value=Path("never-exists-panipani.json"))):
            stream = StringIO()
            with redirect_stdout(stream):
                daily_reel.guard()
            self.assertIn("should_publish=false", stream.getvalue())

    def test_enabled_manual_without_record_allows_one_slot(self):
        from io import StringIO
        from contextlib import redirect_stdout
        from unittest.mock import patch
        info = {"day": "2026-10-14", "slot": "1800", "key": "2026-10-14_1800"}
        with (patch.dict(os.environ, {"GITHUB_EVENT_NAME":"workflow_dispatch", "PANIPANI_PUBLICATION_ENABLED":"true"}),
              patch.object(daily_reel, "context", return_value=info),
              patch.object(daily_reel, "state_file", return_value=Path("never-exists-panipani.json"))):
            stream = StringIO()
            with redirect_stdout(stream):
                daily_reel.guard()
            self.assertIn("should_publish=true", stream.getvalue())

class DelayedCronTests(unittest.TestCase):
    def test_late_noon_trigger_selects_current_evening_slot(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from unittest.mock import patch
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME":"schedule", "GITHUB_EVENT_SCHEDULE":"5 3 * * *", "POST_SLOT_OVERRIDE":""}):
            with patch.object(daily_reel, "datetime", wraps=datetime) as clock:
                clock.now.return_value=datetime(2026,10,14,19,5,tzinfo=ZoneInfo("Asia/Tokyo"))
                info=daily_reel.context()
                self.assertEqual(info["slot"],"1800")
                self.assertTrue(daily_reel.scheduled_window_is_valid(info,clock.now.return_value))
    def test_hourly_check_does_not_publish_before_first_slot(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from unittest.mock import patch
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME":"schedule", "GITHUB_EVENT_SCHEDULE":"17 * * * *", "POST_SLOT_OVERRIDE":""}):
            with patch.object(daily_reel, "datetime", wraps=datetime) as clock:
                clock.now.return_value=datetime(2026,10,14,4,17,tzinfo=ZoneInfo("Asia/Tokyo"))
                self.assertFalse(daily_reel.scheduled_window_is_valid(daily_reel.context(),clock.now.return_value))
    def test_selected_slot_remains_pinned_after_clock_advances(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME":"schedule", "GITHUB_EVENT_SCHEDULE":"17 * * * *", "POST_SLOT_OVERRIDE":"1800"}):
            self.assertEqual(daily_reel.context()["slot"],"1800")

if __name__ == "__main__":
    unittest.main()
