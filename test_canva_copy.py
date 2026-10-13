"""Contract checks for editable Canva template text across all topic rotations."""
import unittest
from daily_topics import TOPICS
from canva_copy import (
    MICRO_PROMPTS, MAX_LENGTH, CopyLayoutError,
    make_visual_copy, validate_topic_bank
)

class CanvaMicrocopyTests(unittest.TestCase):
    def test_all_86_topics_have_reviewed_visual_copy(self):
        self.assertEqual(validate_topic_bank(), 86)
        self.assertEqual(len(MICRO_PROMPTS), 86)

    def test_every_topic_fits_each_shared_field_limit(self):
        for topic in TOPICS:
            with self.subTest(topic=topic[0]):
                fields = make_visual_copy(*topic)
                self.assertEqual(set(fields), set(MAX_LENGTH))
                self.assertTrue(all(0 < len(s) <= MAX_LENGTH[k] for k,s in fields.items()))
                self.assertNotIn("。", fields["PROMPT"])
                self.assertTrue(fields["CTA"].startswith("保存"))
                self.assertNotEqual(fields["PROMPT"], topic[2])

    def test_example_has_short_japanese_fields(self):
        fields = make_visual_copy(
            "長文の要約", "読む前に概要を把握",
            "次の文章を要点3つと、確認したい疑問2つに整理してください。",
            "原文と必ず照合",
        )
        self.assertEqual(fields["HOOK"], "読む前に概要を把握")
        self.assertEqual(fields["PROMPT"], "要点を3つにする")
        self.assertEqual(fields["CAUTION"], "原文と必ず照合")

    def test_new_unreviewed_topic_is_rejected(self):
        with self.assertRaisesRegex(CopyLayoutError, "Unreviewed"):
            make_visual_copy("未確認のテーマ","悩み","出力して","気をつける")

    def test_overlong_and_blank_hooks_rejected(self):
        for hook in ("大切なことを何よりも先に全部丁寧に整理しよう", "\n \t"):
            with self.subTest(hook=hook):
                with self.assertRaises(CopyLayoutError):
                    make_visual_copy("メール返信", hook, "メール返信を作る", "宛名と期限を確認")

if __name__ == "__main__":
    unittest.main()
