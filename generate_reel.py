"""Generate an original Japanese vertical MP4 in GitHub Actions without external media hosts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, shutil, datetime

OUT=Path("output")
OUT.mkdir(exist_ok=True)
W,H=720,1280
FONT_CANDIDATES=[
"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
"/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
]
font_path=next((p for p in FONT_CANDIDATES if Path(p).exists()),None)
if not font_path: raise RuntimeError("Japanese font not installed")
def font(size): return ImageFont.truetype(font_path,size)
slides=[
("AIでメール返信","毎回ゼロから書かなくてOK"),
("最初に要点を整理","相手・目的・結論を確認"),
("AIへの依頼文","丁寧な返信を150字以内で作成"),
("最後は人が確認","名前・日時・事実をチェック"),
("保存して使おう","Panipani / AI活用Tips")
]
frames=[]
for i,(head,sub) in enumerate(slides):
    img=Image.new("RGB",(W,H),(12,20,45))
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((38,80,682,1200),radius=34,fill=(24,38,78),outline=(80,120,210),width=3)
    d.text((70,135),"PANIPANI  |  AI TIPS",font=font(28),fill=(115,205,255))
    d.multiline_text((70,330),head,font=font(58),fill="white",spacing=20)
    d.rounded_rectangle((65,580,655,900),radius=24,fill=(37,58,105))
    d.multiline_text((88,680),sub,font=font(34),fill=(235,244,255),spacing=15)
    d.text((70,1090),f"{i+1} / {len(slides)}",font=font(28),fill=(150,195,240))
    p=OUT/f"slide_{i:02}.png";img.save(p);frames.append(p)
if not shutil.which("ffmpeg"):raise RuntimeError("ffmpeg unavailable")
clips=[]
for i,p in enumerate(frames):
    clip=OUT/f"clip_{i:02}.mp4"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-loop","1","-framerate","24","-i",str(p),"-t","4","-vf","scale=1080:1920,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","23","-r","24","-an",str(clip)],check=True)
    clips.append(clip)
manifest=OUT/"concat.txt"
manifest.write_text("".join("file '"+p.name+"'\n" for p in clips),encoding="utf-8")
dest=OUT/"panipani_reel.mp4"
subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(manifest),"-c","copy","-movflags","+faststart",str(dest)],check=True)
print("Generated:",dest,"bytes:",dest.stat().st_size)
