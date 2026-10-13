"""Use a verified previously exported genuine Canva video for tonight's second post."""
import hashlib,json,sys,shutil
from pathlib import Path
import canva_connect_export as ce
import daily_reel
TITLE="クレーム返信"
SHA="b6b09338cc7d814dd86df43a5eb11d40c842997a38d9b4b10bd43de286761bea"
CAPTION="""クレームへの返信、焦って送る前に。

AIで下書きを作るなら、相手の困りごと・確認済みの事実・こちらが対応できる範囲を分けて渡すと整理しやすくなります。

コピペ用👇
「次の問い合わせへの返信案を、丁寧で落ち着いた文体で作ってください。相手の困りごとへの理解、確認済みの事実、次の対応の順に整理してください。未確認の原因は断定せず、できると確認していない返金・交換・期限は約束しないでください。
［個人情報を伏せた問い合わせ本文］
［確認済みの事実と対応できる範囲］」

送信前に、宛名・事実・対応範囲を必ず確認しましょう。
※画面はCanvaで制作した説明用イメージです。
#AI活用 #ChatGPT活用 #仕事効率化 #メール返信 #Panipani"""
def main():
 if sys.argv[1]=="record":
  original=daily_reel.context
  def context():
   info=original();info["topic"]=(TITLE,"冷静に対応する","丁寧な返信を作る","約束前に確認");return info
  daily_reel.context=context;daily_reel.record();return
 info=daily_reel.context()
 if daily_reel.state_file(info).exists():raise RuntimeError("Already recorded")
 root=Path("reviewed_canva")
 manifest=json.loads((root/"manifest.json").read_text())
 row=next(x for x in manifest["results"] if x["template"]=="DAHX1vFRj1g")
 src=root/"DAHX1vFRj1g.mp4"
 if row["sha256"]!=SHA or hashlib.sha256(src.read_bytes()).hexdigest()!=SHA:raise RuntimeError("Source checksum mismatch")
 name="panipani-20261013_1800-canva-complaint.mp4"
 dest=Path("site/reels")/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 ce.normalize_audio(dest);ce.verify_video(dest)
 ce.write_provenance(dest,row["template"],row["new_design"],row["canva_export_job"])
 Path("output/filename.txt").write_text(name)
 Path("output/caption.txt").write_text(CAPTION)
 Path("site/index.html").write_text("<!doctype html><title>Panipani</title>")
if __name__=="__main__":main()
