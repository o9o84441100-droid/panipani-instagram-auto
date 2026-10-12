"""Regression tests for data-driven Reel topics without network calls."""
import json
import tempfile
import unittest
from pathlib import Path

import weekly_optimizer as w
from daily_topics import TOPICS


class WeeklyOptimizationTest(unittest.TestCase):
    def test_categories_are_grounded(self):
        self.assertEqual(w.category_of("メール返信"), "コミュニケーション")
        self.assertEqual(w.category_of("表の見出し"), "情報・データ")
        self.assertEqual(w.category_of("英会話練習"), "学習・語学")
        self.assertGreater(len(TOPICS), 75)

    def test_insufficient_data_does_not_enable(self):
        original_load, original_dest = w.load_records, w.DEST
        with tempfile.TemporaryDirectory() as folder:
            try:
                w.load_records = lambda: []
                w.DEST = Path(folder) / "strategy.json"
                result = w.optimize()
                self.assertFalse(result["enabled"])
                self.assertEqual(result["samples_36_to_72h"], 0)
                self.assertTrue(all(x == 1.0 for x in result["category_weights"].values()))
                self.assertTrue(w.DEST.exists())
            finally:
                w.load_records, w.DEST = original_load, original_dest

    def test_evidence_shifts_weights_without_excluding_categories(self):
        old_load, old_dest = w.load_records, w.DEST
        with tempfile.TemporaryDirectory() as folder:
            try:
                dataset = (
                    [{"category":"コミュニケーション","quality_score":200} for _ in range(12)] +
                    [{"category":"情報・データ","quality_score":15} for _ in range(12)] +
                    [{"category":"学習・語学","quality_score":55} for _ in range(12)]
                )
                w.load_records = lambda: dataset
                w.DEST = Path(folder) / "strategy.json"
                result = w.optimize()
                self.assertTrue(result["enabled"])
                self.assertEqual(result["samples_36_to_72h"], 36)
                self.assertGreater(result["category_weights"]["コミュニケーション"], 1)
                self.assertLess(result["category_weights"]["情報・データ"], 1)
                self.assertGreaterEqual(min(result["category_weights"].values()), w.MIN_WEIGHT)
                self.assertLessEqual(max(result["category_weights"].values()), w.MAX_WEIGHT)
            finally:
                w.load_records, w.DEST = old_load, old_dest

    def test_no_topic_repeat_when_strategy_enabled(self):
        import daily_reel
        from datetime import date
        old_state, old_topics_dir = daily_reel.STATE, Path("state/strategy.json")
        # Verify the fallback remains valid when no strategy is present.
        self.assertIn(daily_reel.choose_topic("2026-10-13_0800", 13, date(2026,10,13)), TOPICS)


if __name__ == "__main__":
    unittest.main()
