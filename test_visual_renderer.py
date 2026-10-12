"""Regression checks for Canva-inspired creative storyboards, no Instagram publish."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import visual_renderer as v

INFO = {
    "key": "2026-10-13_0800",
    "topic": ("メール返信", "返信文が浮かばない？",
              "次のメールへの返信を、丁寧で簡潔な150字以内の文面にしてください。事実は加えないでください。",
              "宛名と期限を確認"),
    "color": ((11, 24, 54), (62, 50, 143), (129, 198, 255)),
}

class VisualCreativeTests(unittest.TestCase):
    def test_six_rotating_storyboards(self):
        patterns = set()
        for n in range(6):
            info = dict(INFO)
            info["key"] = "2026-10-13_" + str(1000+n)
            with tempfile.TemporaryDirectory() as temp:
                images, storyboard = v.build(info, temp)
                self.assertEqual(len(images), 5)
                self.assertEqual(len(storyboard), 5)
                self.assertEqual(len(set(storyboard)), 5)
                self.assertTrue(any(t in storyboard for t in ("compare", "mock_chat", "steps")))
                patterns.add(tuple(storyboard))
                for im_path in images:
                    with Image.open(im_path) as im:
                        self.assertEqual(im.size, (1080,1920))
                        self.assertEqual(im.mode, "RGB")
                        self.assertGreater(Path(im_path).stat().st_size, 10000)
        self.assertEqual(len(patterns), 6)

    def test_japanese_long_prompts_not_crashing(self):
        info = dict(INFO)
        info["topic"] = ("要件の整理", "依頼が曖昧で困る時",
                         "次の依頼文を対象者・目的・納期・成果物・前提条件と未確認事項に整理して、曖昧な箇所は質問リストにしてください。",
                         "固有名詞と実際の締切は元資料で必ず確認する")
        with tempfile.TemporaryDirectory() as temp:
            files, _ = v.build(info, temp)
            self.assertEqual(len(files), 5)

    def test_different_scenes_are_visually_distinct(self):
        with tempfile.TemporaryDirectory() as temp:
            images, _ = v.build(INFO, temp)
            sigs = set()
            for path in images:
                sigs.add(hashlib.sha256(Path(path).read_bytes()).hexdigest())
            self.assertEqual(len(sigs), 5)

if __name__ == "__main__":
    unittest.main()
