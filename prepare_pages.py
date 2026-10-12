"""Prepare a publicly downloadable but non-sensitive Reel asset for GitHub Pages.
Publishes NO content to Instagram. The GitHub Pages workflow is responsible for deployment.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path("site")
REELS = ROOT / "reels"
REELS.mkdir(parents=True, exist_ok=True)
key = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d-%H%M")
# Build the same kind of MP4 already verified in the previous GitHub Actions run.
subprocess.run([sys.executable, "generate_reel.py"], check=True)
source = Path("output/panipani_reel.mp4")
if not source.exists() or source.stat().st_size < 10000:
    raise RuntimeError("MP4 generation did not produce a valid nonempty video")
name = f"panipani-{key}-{os.getenv('GITHUB_RUN_ID', 'local')}.mp4"
shutil.copyfile(source, REELS / name)
(ROOT / "index.html").write_text(
    "<!doctype html><html lang='ja'><meta charset='utf-8'><title>Panipani Reels</title>"
    "<meta name='robots' content='noindex'><body>Panipani video asset hosting</body></html>",
    encoding="utf-8"
)
Path("video_filename.txt").write_text(name, encoding="utf-8")
Path("caption.txt").write_text(
    "メール返信をAIでラクにするコツ。\n"
    "要点を整理してから、150文字以内の丁寧な返信案を作成。\n"
    "送る前に名前・日時・事実関係を確認しよう。\n\n"
    "使える依頼例：\n"
    "「次の内容をもとに、丁寧で簡潔なメール返信案を150文字以内で作ってください。"
    "事実を推測して追加せず、不明点は確認事項として示してください。」\n\n"
    "#AI活用 #ChatGPT活用 #仕事効率化 #Panipani",
    encoding="utf-8"
)
print("Prepared public-only MP4:", name, "bytes:", (REELS / name).stat().st_size)
