"""Panipani scheduled Reel builder and durable publication ledger.
Works without paid generation APIs; new captions are selected from the curated topic bank.
"""
import json
import math
import os
import random
import hashlib
from pathlib import Path
import subprocess
import sys
import wave
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from daily_topics import TOPICS
from weekly_optimizer import category_of

JST = ZoneInfo("Asia/Tokyo")
SLOTS = ("0800", "1000", "1200", "1800", "2100")
CRON_TO_SLOT = {
    "5 23 * * *": "0800",
    "5 1 * * *": "1000",
    "5 3 * * *": "1200",
    "5 9 * * *": "1800",
    "5 12 * * *": "2100",
}
ROOT = Path("output")
STATE = Path("state/posts")
WIDTH, HEIGHT = 1080, 1920
STYLES = [
    ("これ、AIに頼もう", "今日から使えるAI活用Tips"),
    ("コピペで使える", "忙しい人向けAI活用Tips"),
    ("ちょっとラクになる", "実務で役立つAI活用Tips"),
]
COLORS = [
    ((11, 24, 54), (62, 50, 143), (129, 198, 255)),
    ((14, 38, 59), (19, 91, 115), (120, 241, 225)),
    ((31, 23, 60), (113, 51, 123), (238, 165, 255)),
    ((12, 36, 47), (60, 90, 90), (246, 209, 125)),
]


def choose_topic(key, serial, today):
    base = TOPICS[serial % len(TOPICS)]
    path = Path("state/strategy.json")
    if not path.exists():
        return base
    try:
        strategy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return base
    if not strategy.get("enabled"):
        return base
    weights = strategy.get("category_weights") or {}
    used = set()
    cutoff = today - timedelta(days=14)
    for marker_path in STATE.glob("????-??-??_????.json"):
        try:
            day = date.fromisoformat(marker_path.name[:10])
            if day >= cutoff:
                used.add(json.loads(marker_path.read_text(encoding="utf-8")).get("topic"))
        except (ValueError, OSError):
            continue
    candidates = [topic for topic in TOPICS if topic[0] not in used]
    if not candidates:
        return base
    seed = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    generator = random.Random(seed)
    def priority(topic):
        value = weights.get(category_of(topic[0]), 1.0)
        weight = min(1.4, max(.78, float(value)))
        return generator.random() ** (1.0 / weight)
    return max(candidates, key=priority)


def context():
    today = datetime.now(JST).date()
    cron = os.getenv("GITHUB_EVENT_SCHEDULE", "").strip()
    event = os.getenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    if event == "schedule":
        if cron not in CRON_TO_SLOT:
            raise RuntimeError("Unknown scheduled cron: " + repr(cron))
        slot = CRON_TO_SLOT[cron]
    else:
        slot = os.getenv("MANUAL_SLOT", "0800").strip() or "0800"
    if slot not in SLOTS:
        raise RuntimeError("Unknown slot: " + slot)
    key = today.strftime("%Y-%m-%d") + "_" + slot
    serial = (today - date(2026, 10, 13)).days * len(SLOTS) + SLOTS.index(slot) + 13
    item = choose_topic(key, serial, today)
    # Rotate creative hooks every upload instead of repeating one format for 17 days.
    style = STYLES[serial % len(STYLES)]
    color = COLORS[serial % len(COLORS)]
    return {"day": str(today), "slot": slot, "key": key,
            "topic": item, "style": style, "color": color}


def state_file(info):
    return STATE / (info["key"] + ".json")


def guard():
    info = context()
    done = state_file(info).exists()
    print("slot_key=" + info["key"])
    print("should_publish=" + ("false" if done else "true"))
    print("Existing published slot" if done else "Unpublished slot; eligible for processing", file=sys.stderr)


def write_lines(draw, text, pos, max_width, font, fill, gap=14, max_lines=9):
    x, y = pos
    lines = []
    current = ""
    for ch in text:
        if ch == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = current + ch
        if draw.textbbox((0, 0), candidate, font=font)[2] > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = candidate
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        raise ValueError("Text exceeds safety margin; do not truncate Japanese text")
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + gap
    return y


def render_frame(info, slide_no, header, body, footer):
    from PIL import Image, ImageDraw, ImageFont
    regular = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    bold = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    if not Path(regular).exists():
        raise RuntimeError("Japanese Noto CJK font missing")
    if not Path(bold).exists():
        bold = regular
    def font(size, heavy=False):
        return ImageFont.truetype(bold if heavy else regular, size)
    bg, center, accent = info["color"]
    image = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        t = y / HEIGHT
        shade = tuple(round(bg[i] * (1 - t) + center[i] * t) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=shade)
    # Decorative orbital geometry; no stock media, third-party imagery, or hidden data.
    draw.ellipse((720, 115, 1440, 835), outline=accent, width=6)
    draw.ellipse((-370, 1230, 310, 1900), outline=accent, width=4)
    # High-contrast Canva-inspired editorial system with rotating layout treatments.
    treatment = (int(info["key"].replace("-", "").replace("_", "")) + slide_no) % 3
    card_fill = [(19, 31, 60), (25, 39, 68), (17, 45, 67)][treatment]
    draw.rounded_rectangle((58, 138, 1022, 1590), radius=54, fill=card_fill,
                           outline=tuple(min(255, int(x * .75)) for x in accent), width=3)
    draw.rounded_rectangle((92, 193, 456, 265), radius=32, fill=accent)
    draw.text((121, 205), "PANIPANI  /  AI", font=font(32, True), fill=bg)
    draw.text((98, 317), f"0{slide_no}  /  05", font=font(37), fill=accent)
    # Screen-edge safe areas: do not put essential copy at the bottom/right UI overlay.
    title_x = 105 if treatment != 1 else 128
    heading_size = 78 if len(header) < 15 else 67
    header_end = write_lines(draw, header, (title_x, 425), 830,
                             font(heading_size, True), (255, 255, 255), 22, 3)
    body_size = 55 if len(body) < 38 else (49 if len(body) < 75 else 44)
    body_y = max(765, header_end + 80)
    draw.rounded_rectangle((92, body_y - 28, 978, 1460), radius=36,
                           fill=[(32, 49, 84), (35, 51, 77), (30, 57, 78)][treatment])
    draw.rounded_rectangle((112, body_y + 10, 122, min(body_y + 170, 1420)),
                           radius=4, fill=accent)
    write_lines(draw, body, (145, body_y + 32), 770,
                font(body_size), (236, 244, 255), 21, 10)
    draw.text((106, 1510), footer[:28], font=font(29), fill=accent)
    for k in range(5):
        draw.rounded_rectangle((104 + 175 * k, 1720, 258 + 175 * k, 1732), radius=7,
                               fill=accent if k <= slide_no - 1 else (60, 78, 105))
    return image


def make_audio(destination):
    """Original low-volume tones composed algorithmically; no third-party music."""
    rate = 24000
    seconds = 20
    notes = [196.0, 246.94, 293.66, 246.94, 220.0]
    with wave.open(str(destination), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for n in range(rate * seconds):
            t = n / rate
            beat = int(t / 4)
            f = notes[min(4, beat)]
            fade = min(1., t / .6, (seconds - t) / .8)
            pulse = .66 + .34 * (0.5 + 0.5 * math.sin(2 * math.pi * .5 * t))
            v = fade * pulse * (
                .07 * math.sin(2 * math.pi * f * t) +
                .022 * math.sin(2 * math.pi * (f * 1.5) * t)
            )
            wf.writeframesraw(int(max(-32760, min(32760, v * 32767))).to_bytes(
                2, byteorder="little", signed=True))


def prepare():
    info = context()
    if state_file(info).exists():
        raise RuntimeError("This slot has already been recorded; refuse duplicate build")
    ROOT.mkdir(exist_ok=True)
    site = Path("site")
    public = site / "reels"
    public.mkdir(parents=True, exist_ok=True)
    title, situation, prompt, caution = info["topic"]
    tagline, subtitle = info["style"]
    # Native 1080x1920 motion-graphic storyboards: no Canva access token or paid API.
    # Import Pillow here, not at module import time: the light-weight scheduled guard
    # does not install Pillow, and it must never fail simply from a missing renderer.
    from visual_renderer import build as build_visual_storyboard
    frames, scene_types = build_visual_storyboard(info, ROOT)
    mode = int(info["key"].replace("-", "").replace("_", "")) % 4
    print("Creative storyboard:", " -> ".join(scene_types))
    parts = []
    for i, p in enumerate(frames, 1):
        clip = ROOT / f"part_{i:02}.mp4"
        # A subtle camera pan adds motion while keeping large Japanese text readable.
        # Vertical and horizontal movements alternate; pan never exceeds 3% of canvas.
        travel = "min((iw-ow), (iw-ow)*t/4)" if (i + mode) % 2 == 0 else "max(0, (iw-ow)*(1-t/4))"
        vertical = "min((ih-oh), (ih-oh)*t/4)" if (i + mode) % 3 == 0 else "(ih-oh)/2"
        motion = ("scale=1112:1978,"
                  "crop=1080:1920:x='" + travel + "':y='" + vertical + "',"
                  "format=yuv420p")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-loop", "1", "-framerate", "24", "-i", str(p),
                        "-vf", motion, "-t", "4", "-c:v", "libx264",
                        "-preset", "veryfast", "-crf", "25",
                        "-pix_fmt", "yuv420p", "-r", "24", str(clip)],
                       check=True)
        parts.append(clip)
    playlist = ROOT / "parts.txt"
    playlist.write_text("".join("file '" + p.name + "'\n" for p in parts), encoding="utf-8")
    background = ROOT / "background.wav"
    make_audio(background)
    filename = "panipani-" + info["key"].replace("-", "") + ".mp4"
    dest = public / filename
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "concat", "-safe", "0", "-i", str(playlist),
                    "-i", str(background), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                    "-t", "20", "-movflags", "+faststart", str(dest)], check=True)
    size = dest.stat().st_size
    if size < 20000:
        raise RuntimeError("Final Reel MP4 is unexpectedly small")
    (site / "index.html").write_text(
        "<!doctype html><html lang='ja'><meta charset='utf-8'><title>Panipani</title>"
        "<meta name='robots' content='noindex'><body>Panipani video delivery</body></html>",
        encoding="utf-8")
    caption = (f"【AI活用Tips】{title}をもっとラクに！\n\n"
               f"こんな時に：{situation}\n\n"
               f"▼ AIにコピペして使える依頼文\n{prompt}\n\n"
               f"最後に確認：{caution}\n\n"
               "AIの出力は下書き。事実・個人情報・固有名詞は自分でチェック。\n"
               "よかったら保存して試してみてね！\n\n"
               f"#AI活用 #ChatGPT活用 #仕事効率化 #Panipani #AI時短")
    (ROOT / "caption.txt").write_text(caption, encoding="utf-8")
    (ROOT / "filename.txt").write_text(filename, encoding="utf-8")
    (ROOT / "slot_key.txt").write_text(info["key"], encoding="utf-8")
    print(f"Prepared {info['key']}: {title}, MP4 size={size} bytes, filename={filename}")


def record():
    info = context()
    result_path = ROOT / "publish_result.json"
    if not result_path.exists():
        raise RuntimeError("No publication result to record")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("status") not in ("published", "existing") or not result.get("id"):
        raise RuntimeError("Cannot confirm publication. Not recording slot as complete.")
    STATE.mkdir(parents=True, exist_ok=True)
    filename = ROOT / "filename.txt"
    marker = {
        "date": info["day"], "slot": info["slot"], "topic": info["topic"][0],
        "style": info["style"][0], "category": category_of(info["topic"][0]),
        "media_id": result["id"], "permalink": result.get("permalink"),
        "status": result["status"],
        "run_id": os.getenv("GITHUB_RUN_ID", "unknown"),
        "video_filename": filename.read_text(encoding="utf-8").strip(),
        "recorded_at": datetime.now(JST).isoformat()
    }
    marker_path = state_file(info)
    if marker_path.exists():
        raise RuntimeError("Slot marker already exists; no overwrite")
    marker_path.write_text(json.dumps(marker, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("Recorded published Reel:", marker_path, marker["media_id"])
    if marker["permalink"]:
        print("Instagram Reel URL:", marker["permalink"])


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("guard", "prepare", "record"):
        raise RuntimeError("Use: python daily_reel.py guard|prepare|record")
    globals()[sys.argv[1]]()


if __name__ == "__main__":
    main()
