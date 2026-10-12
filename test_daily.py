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

if __name__ == "__main__":
    unittest.main()
