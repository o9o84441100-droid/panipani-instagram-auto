"""One owner-authorized real-photo Canva export, not a Canva API export."""
import hashlib,json,os,sys,time,subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import publisher
JST=ZoneInfo("Asia/Tokyo")
SRC=Path("approved_media/realphoto-20261013.mp4")
SOURCE_SHA="119d4635ffacc495224ce10ed38eb22328f2a7155a682a4d6a7efcb369bac405"
LEDGER=Path("state/posts/realphoto_20261013_2300.json")
CAPTION="""心地よく暮らす、小さな習慣5選。

暮らしを整えたい日に、できそうなものを一つだけ。

① よく使う物の置き場所を決める
② 寝る前にテーブルの上を片づける
③ 翌日のやることを3つだけ書く
④ 共有する予定を一か所にまとめる
⑤ 一度に変えすぎず、続けやすいことから始める

AIを使うなら、③の整理にも。
「次のやることから、明日優先する3つを整理してください。期限が不明なものは推測せず、確認が必要と書いてください」

※映像はCanvaの実写背景テンプレートを使ったイメージです。動画内の「都内、2人暮らしの場合」はテンプレートの例示で、投稿者本人の居住地・同居状況を示すものではありません。

保存して、できそうなことから試してみてください。
#暮らしを整える #小さな習慣 #AI活用 #Panipani"""
def check_date():
 now=datetime.now(JST)
 if now.strftime("%Y-%m-%d")!="2026-10-13":raise RuntimeError("Authorization expired")
 return now
def prepare():
 check_date()
 if LEDGER.exists():raise RuntimeError("Already published")
 if hashlib.sha256(SRC.read_bytes()).hexdigest()!=SOURCE_SHA:raise RuntimeError("Owner supplied source checksum mismatch")
 dest=Path("site/reels/panipani-realphoto-20261013-2300.mp4")
 dest.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(SRC),"-vf","scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",str(dest)],check=True)
 Path("output").mkdir(exist_ok=True)
 Path("output/caption.txt").write_text(CAPTION)
 Path("output/filename.txt").write_text(dest.name)
 Path("output/owner_source.json").write_text(json.dumps({"source":"owner_supplied_canva_export","canva_design_id":"DAHX5ScAlSk","source_sha256":SOURCE_SHA,"video_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"background":"real_photo","resolution_note":"Owner file 512x910 scaled to delivery dimensions; detail not increased"},indent=2))
 Path("site/index.html").write_text("<!doctype html><title>Panipani</title>")
def wait():
 while True:
  now=check_date()
  if now.hour>=23:break
  time.sleep(min(30,max(1,(datetime(2026,10,13,23,tzinfo=JST)-now).total_seconds())))
 if LEDGER.exists():raise RuntimeError("Already published")
def validate_owner_source():
 check_date()
 if datetime.now(JST).hour<23:raise RuntimeError("Too early")
 if LEDGER.exists():raise RuntimeError("Already published")
 if hashlib.sha256(SRC.read_bytes()).hexdigest()!=SOURCE_SHA:raise RuntimeError("Source mismatch")
 record=json.loads(Path("output/owner_source.json").read_text())
 dest=Path("site/reels")/Path("output/filename.txt").read_text().strip()
 if hashlib.sha256(dest.read_bytes()).hexdigest()!=record["video_sha256"]:raise RuntimeError("Delivery mismatch")
 print("Validated owner-supplied genuine Canva template video; not an API export")
def publish():
 publisher.require_canva_provenance=validate_owner_source
 publisher.main()
def record():
 result=json.loads(Path("output/publish_result.json").read_text())
 if not result.get("id"):raise RuntimeError("No media ID")
 LEDGER.parent.mkdir(exist_ok=True,parents=True)
 LEDGER.write_text(json.dumps({**result,"source":"owner_supplied_canva_export","canva_design_id":"DAHX5ScAlSk","background":"real_photo","recorded_at":datetime.now(JST).isoformat(),"run_id":os.getenv("GITHUB_RUN_ID")},ensure_ascii=False,indent=2))
if __name__=="__main__":globals()[sys.argv[1]]()
