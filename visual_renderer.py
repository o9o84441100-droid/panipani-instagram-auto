"""Original mobile-first motion graphic storyboards inspired by Canva design studies.

Renders editable-by-code 1080x1920 frame assets for independent FFmpeg animation.
No external downloads, image credits, subscription or Canva OAuth required.
This is an original local renderer, NOT an automated Canva export.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
if not Path(REG).exists():
    raise RuntimeError("Noto Sans CJK Regular font required for Japanese text")
if not Path(BOLD).exists():
    BOLD = REG

def F(size, heavy=False):
    return ImageFont.truetype(BOLD if heavy else REG, int(size))

def brighten(c, amount):
    return tuple(max(0, min(255, round(x * (1 - amount) + 255 * amount))) for x in c)

def dim(c, amount):
    return tuple(max(0, min(255, round(x * (1 - amount)))) for x in c)

def surface(colors, variant, scene):
    deep, middle, tint = colors
    backgrounds = [
        (deep, middle),
        (dim(middle, .42), deep),
        (dim(tint, .83), middle),
        (deep, dim(middle, .5)),
        (dim(middle, .48), dim(tint, .81)),
        (dim(tint, .84), deep),
    ]
    c0, c1 = backgrounds[(variant + scene) % len(backgrounds)]
    img = Image.new("RGB", (W, H), c0)
    d = ImageDraw.Draw(img)
    for y in range(H):
        a = y / (H - 1)
        color = tuple(round(c0[k] * (1 - a) + c1[k] * a) for k in range(3))
        d.line((0, y, W, y), fill=color)
    # Subtle original procedural decor, entirely within ownership of this project.
    d.ellipse((760, 65, 1420, 725), outline=dim(tint, .62), width=5)
    d.ellipse((-290, 1290, 390, 1980), outline=dim(tint, .65), width=4)
    for n in range(9):
        yy = 265 + n * 120
        d.line((45, yy, W - 45, yy), fill=tuple(min(255, x + 5) for x in deep), width=1)
    return img, d

def line_break(d, value, font, max_w, max_lines=6):
    value = str(value)
    lines = []
    for raw in value.split("\n"):
        if not raw:
            lines.append("")
            continue
        line = ""
        for ch in raw:
            candidate = line + ch
            if line and d.textbbox((0, 0), candidate, font=font)[2] > max_w:
                lines.append(line)
                line = ch
            else:
                line = candidate
        if line:
            lines.append(line)
    if len(lines) > max_lines:
        # Meaningful excerpt for very short video; caption always has complete text.
        lines = lines[:max_lines]
        if lines[-1] and len(lines[-1]) > 1:
            lines[-1] = lines[-1][:-1] + "…"
    return lines

def txt(d, value, x, y, size, color, width=800, weight=False, gap=15, limit=6):
    font = F(size, weight)
    lines = line_break(d, value, font, width, limit)
    for line in lines:
        d.text((x, y), line, fill=color, font=font,
               stroke_width=0)
        y += int(size + gap)
    return y

def panel(d, bounds, fill, stroke=None, radius=35, border=2):
    d.rounded_rectangle(bounds, radius=radius, fill=fill,
                        outline=stroke, width=border if stroke else 1)

def shell(d, info, variant, slide):
    accent = info["color"][2]
    white = (248, 250, 255)
    muted = (163, 184, 211)
    label_bg = dim(accent, .15)
    panel(d, (80, 115, 515, 198), label_bg, radius=38)
    txt(d, "PANIPANI  /  AI TIPS", 107, 131, 31, info["color"][0], 360, True)
    txt(d, f"0{slide}   /   05", 790, 145, 29, accent, 205, True)
    # Instagram-safe: keep body copy above 1500 and away from right UI column.
    panel(d, (79, 1550, 1005, 1560), dim(accent, .55), radius=5)
    progress = 926 * (slide / 5)
    panel(d, (79, 1550, int(79 + progress), 1560), accent, radius=5)
    txt(d, "保存して後で使おう", 92, 1620, 37, muted, 760)
    return white, muted, accent

def cover(d, info, variant, title, situation, white, muted, accent):
    """Six independent hero treatments, selected by daily variant."""
    headline = situation if len(situation) < 19 else title + "で迷ってない？"
    if variant % 2:
        panel(d, (100, 335, 975, 1260), dim(accent, .81), stroke=dim(accent, .4), radius=72)
        d.polygon([(114, 520), (215, 505), (215, 610), (114, 627)], fill=accent)
        txt(d, "こんなとき、AI。", 150, 710, 72, accent, 700, True, 22)
        txt(d, headline, 148, 900, 81, white, 745, True, 26, 3)
    else:
        panel(d, (100, 408, 980, 518), dim(accent, .1), radius=30)
        txt(d, "今日のAI活用", 145, 432, 42, info["color"][0], 680, True)
        txt(d, headline, 105, 650, 94, white, 820, True, 20, 4)
        panel(d, (108, 1080, 880, 1220), dim(accent, .78), radius=39)
        txt(d, "1つ覚えると、作業がラクに", 145, 1110, 45, accent, 705, True)

def compare(d, info, title, prompt, white, muted, accent):
    txt(d, "BEFORE  /  AFTER", 102, 320, 57, accent, 780, True)
    panel(d, (95, 485, 990, 845), (51, 62, 81), radius=42)
    panel(d, (123, 525, 347, 585), (102, 55, 67), radius=18)
    txt(d, "BEFORE", 144, 534, 26, white, 180, True)
    txt(d, "ざっくりまとめて", 140, 657, 59, white, 780, True)
    d.line((420, 872, 565, 943), fill=accent, width=14)
    d.line((565, 943, 490, 943), fill=accent, width=14)
    d.line((565, 943, 553, 869), fill=accent, width=14)
    panel(d, (95, 1000, 990, 1450), (20, 67, 72), stroke=accent, radius=42, border=3)
    panel(d, (125, 1038, 347, 1102), accent, radius=18)
    txt(d, "AFTER", 148, 1045, 27, info["color"][0], 160, True)
    txt(d, prompt, 137, 1152, 41, white, 760, False, 15, 5)

def mock_chat(d, info, title, situation, white, muted, accent):
    txt(d, "AIへの頼み方を変える", 103, 325, 65, white, 840, True)
    panel(d, (192, 465, 908, 1464), (9, 23, 44), stroke=dim(accent, .45), radius=85, border=9)
    panel(d, (420, 492, 678, 522), (3, 9, 24), radius=14)
    txt(d, "画面イメージ", 237, 548, 29, muted, 410)
    panel(d, (250, 669, 805, 862), (49, 61, 85), radius=34)
    txt(d, situation, 286, 721, 44, white, 470, False, 12, 3)
    panel(d, (305, 920, 860, 1275), dim(accent, .67), stroke=accent, radius=34)
    txt(d, "AIへの指示", 350, 968, 34, accent, 445, True)
    txt(d, f"「{title}」\n目的・条件・形式を\n指定してみよう", 348, 1050, 43, white, 445, True, 15, 4)
    d.ellipse((475, 1365, 622, 1380), fill=(55, 75, 99))

def steps(d, info, title, white, muted, accent):
    txt(d, f"{title}を3ステップで", 100, 333, 65, white, 820, True, 18, 2)
    labels = [
        ("01", "目的", "何を作りたい？"),
        ("02", "条件", "誰向け？ 何文字？"),
        ("03", "形式", "箇条書き？ 表？"),
    ]
    for index, (num, head, sub) in enumerate(labels):
        top = 560 + index * 275
        panel(d, (110, top, 970, top + 220), (29, 50, 77), stroke=dim(accent, .4), radius=40)
        panel(d, (145, top + 46, 260, top + 155), accent, radius=29)
        txt(d, num, 165, top + 66, 40, info["color"][0], 100, True)
        txt(d, head, 299, top + 36, 54, white, 530, True)
        txt(d, sub, 300, top + 125, 36, muted, 550)

def action(d, info, prompt, white, muted, accent):
    txt(d, "コピペで使える依頼文", 100, 316, 62, white, 844, True)
    panel(d, (97, 508, 978, 1410), (29, 46, 75), stroke=dim(accent, .38), radius=45)
    panel(d, (135, 550, 565, 637), accent, radius=32)
    txt(d, "AIにこう伝えよう", 157, 566, 34, info["color"][0], 365, True)
    txt(d, prompt, 154, 733, 52 if len(prompt) < 58 else 43,
        white, 742, False, 20, 9)
    txt(d, "全文はキャプションに掲載", 128, 1448, 35, accent, 770)

def caution(d, info, text, white, muted, accent):
    txt(d, "最後に、ここは確認！", 108, 347, 68, white, 828, True)
    panel(d, (115, 625, 962, 1295), (30, 51, 78), radius=43)
    d.ellipse((165, 705, 290, 830), outline=accent, width=8)
    d.line((193, 774, 213, 794), fill=accent, width=9)
    d.line((213, 794, 255, 738), fill=accent, width=9)
    txt(d, text, 165, 916, 54, white, 710, True, 24, 5)
    txt(d, "AIの出力は下書き。最終確認は自分で。", 117, 1368, 33, muted, 780)

def finish(d, info, title, white, muted, accent):
    d.ellipse((310, 340, 770, 800), outline=accent, width=16)
    d.line((410, 566, 505, 663), fill=accent, width=19)
    d.line((505, 663, 670, 471), fill=accent, width=19)
    txt(d, "保存して試してみよう", 120, 870, 76, white, 815, True, 24, 3)
    panel(d, (131, 1130, 949, 1300), dim(accent, .74), radius=55)
    txt(d, f"今日のテーマ：{title}", 175, 1177, 48, accent, 720, True, 18, 2)

def build(info, output_dir):
    """Return exactly 5 legible 1080×1920 RGB PNGs with varied compositions."""
    title, situation, prompt, warning = info["topic"]
    serial = int(info["key"].replace("-", "").replace("_", ""))
    variant = serial % 6
    # A video has varied shot compositions, rather than one same-position title card.
    patterns = [
        ("cover", "steps", "action", "caution", "finish"),
        ("cover", "compare", "action", "caution", "finish"),
        ("cover", "mock_chat", "steps", "action", "finish"),
        ("cover", "compare", "mock_chat", "caution", "finish"),
        ("cover", "steps", "mock_chat", "action", "finish"),
        ("cover", "mock_chat", "action", "caution", "finish"),
    ]
    pattern = patterns[variant]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    created = []
    for idx, scene in enumerate(pattern, 1):
        img, d = surface(info["color"], variant, idx)
        white, muted, accent = shell(d, info, variant, idx)
        if scene == "cover":
            cover(d, info, variant, title, situation, white, muted, accent)
        elif scene == "compare":
            compare(d, info, title, prompt, white, muted, accent)
        elif scene == "mock_chat":
            mock_chat(d, info, title, situation, white, muted, accent)
        elif scene == "steps":
            steps(d, info, title, white, muted, accent)
        elif scene == "action":
            action(d, info, prompt, white, muted, accent)
        elif scene == "caution":
            caution(d, info, warning, white, muted, accent)
        elif scene == "finish":
            finish(d, info, title, white, muted, accent)
        file = output / f"frame_{idx:02}.png"
        img.save(file, format="PNG", optimize=True)
        created.append(file)
    return created, pattern


if __name__ == "__main__":
    demo = {"key": "2026-10-13_0800",
            "topic": ("メール返信", "返信文が浮かばない？",
                      "次のメールの返信案を、丁寧な150字で作ってください。", "名前と期限を確認"),
            "color": ((11, 24, 54), (62, 50, 143), (129, 198, 255))}
    files, pattern = build(demo, "output/visual_demo")
    print("Generated", len(files), "frames:", ",".join(pattern))
