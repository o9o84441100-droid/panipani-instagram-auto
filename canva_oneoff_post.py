"""Stage an already-reviewed Canva MP4 for exactly one Instagram test.
Only the signed-off GitHub Actions artifact is accepted. No Instagram API here.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ART = Path("reviewed_canva")
SOURCE = ART / "DAHX1rftBb4.mp4"
SHA = "a861de0c4f13b85d30fe498e158f67369417dc4392bd5894ea8d1b59287114e7"
VIDEO_NAME = "panipani-canva-test-20261013-a861de0c.mp4"
LEDGER = Path("state/posts/canva_public_test_20261013.json")
CAPTION = """【AIで商品説明をもっとラクに！】
商品紹介の文章、どう書けばいいか迷うことない？
AIに「特徴・使う場面・注意点」を整理してもらうと、下書きを作りやすくなるよ。

コピペして使えるプロンプト👇
「次の商品情報をもとに、商品の特徴・使う場面・注意点の順で、初心者にも読みやすい紹介文を作ってください。確認できない性能や効果は追加せず、不明点は確認が必要と書いてください。」

事実関係を必ず確認してから公開しよう。
📌 保存して、次に役立ててね！
※PanipaniのCanva連携テスト投稿
#AI活用 #ChatGPT活用 #仕事効率化 #商品説明 #Panipani"""

def prepare():
    if LEDGER.exists():
        raise RuntimeError("This Canva public test already has a ledger record")
    manifest = json.loads((ART / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "PASS_CANVA_ONLY_NO_INSTAGRAM_PUBLICATION":
        raise RuntimeError("Canva QA manifest is invalid")
    results = manifest.get("results") or []
    if len(results) != 1:
        raise RuntimeError("Expected exactly one reviewed Canva video")
    row = results[0]
    expectations = {
        "template": "DAHX1rftBb4",
        "new_design": "DAHX3BaIUFA",
        "canva_export_job": "86333515-b99c-46e3-a586-6f120b036e86",
        "sha256": SHA,
        "video_file": SOURCE.name,
        "video_bytes": 1288452,
        "duration_seconds": 10.0,
    }
    if any(row.get(k) != v for k,v in expectations.items()):
        raise RuntimeError("Manifest does not match the reviewed Canva render")
    if SOURCE.stat().st_size != 1288452 or hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA:
        raise RuntimeError("Reviewed Canva MP4 does not match pinned SHA-256")
    data = json.loads(subprocess.check_output(
        ["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(SOURCE)]
    ))
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type")=="video"), {})
    audio = next((s for s in streams if s.get("codec_type")=="audio"), {})
    if (video.get("codec_name"),video.get("width"),video.get("height"),audio.get("codec_name")) != ("h264",1080,1920,"aac"):
        raise RuntimeError("Reviewed Canva media is not 1080x1920 H264/AAC")
    dest=Path("site/reels")/VIDEO_NAME
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(SOURCE,dest)
    Path("site/index.html").write_text("<!doctype html><meta charset='utf-8'><title>Panipani</title>\n")
    Path("output").mkdir(exist_ok=True)
    Path("output/caption.txt").write_text(CAPTION+"\n",encoding="utf-8")
    Path("output/filename.txt").write_text(VIDEO_NAME,encoding="utf-8")
    provenance={
        "source":"canva_connect_api",
        "source_template_id":expectations["template"],
        "canva_design_id":expectations["new_design"],
        "canva_export_job_id":expectations["canva_export_job"],
        "video_file":str(dest),
        "video_sha256":SHA,
    }
    Path("output/canva_provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print("Confirmed reviewed official Canva MP4; publishing guard enabled.")

def record():
    result=json.loads(Path("output/instagram_result.json").read_text(encoding="utf-8"))
    media_id=str(result.get("id") or "")
    if not media_id.isdecimal() or result.get("status") not in ("published","published_unverified","existing"):
        raise RuntimeError("Instagram publish result is not confirmed")
    LEDGER.parent.mkdir(parents=True,exist_ok=True)
    LEDGER.write_text(json.dumps({
        "instagram_media_id":media_id,
        "permalink":result.get("permalink"),
        "status":result["status"],
        "source":"official_canva_connect_api",
        "video_sha256":SHA,
        "source_run_id":38347096573,
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Verified Instagram media:", result.get("permalink") or media_id)

if __name__=="__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["record"]:
        record()
    else:
        raise SystemExit("Usage: canva_oneoff_post.py prepare|record")
