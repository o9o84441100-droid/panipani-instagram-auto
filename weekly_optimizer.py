"""Weekly evidence-limited topic optimizer for Panipani.

Learns only from genuine published Instagram media after 36–72 hours.
Never fabricates missing data, and keeps exploration/diversity.
"""
import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
ROOT = Path("state/analytics")
LEDGER = Path("state/posts")
DEST = Path("state/strategy.json")
MIN_POSTS = 30
MIN_PER_CATEGORY = 4
MAX_WEIGHT = 1.40
MIN_WEIGHT = 0.78

CATEGORY_PATTERNS = (
    ("コミュニケーション", ("メール", "返信", "感謝", "お礼", "お断り", "催促", "クレーム",
                        "商談", "面接", "会話", "質問", "案内", "自己紹介")),
    ("情報・データ", ("表", "CSV", "グラフ", "数字", "リサーチ", "比較",
                    "情報", "アンケート", "スプレッド", "資料")),
    ("コンテンツ制作", ("SNS", "動画", "ブログ", "タイトル", "見出し", "コピー",
                     "文章", "商品説明", "ネーミング", "ストーリーズ", "企画")),
    ("学習・語学", ("英語", "単語", "学習", "復習", "読書", "勉強")),
)


def category_of(title):
    if "英会話" in title or "英単語" in title:
        return "学習・語学"
    for category, terms in CATEGORY_PATTERNS:
        if any(term in title for term in terms):
            return category
    return "仕事の効率化"


def parse_time(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(JST)


def load_records():
    snapshots = []
    for path in sorted(ROOT.glob("????-??-??.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
            captured = parse_time(d["checked_at"])
            posts = {str(p["id"]): p for p in (d.get("posts") or [])}
            snapshots.append((captured, posts))
        except (ValueError, OSError, KeyError, TypeError):
            continue
    samples = []
    for path in sorted(LEDGER.glob("????-??-??_????.json")):
        try:
            marker = json.loads(path.read_text(encoding="utf-8"))
            media_id = str(marker["media_id"])
            title = marker["topic"]
        except (ValueError, OSError, KeyError):
            continue
        observations = []
        for captured, posts in snapshots:
            media = posts.get(media_id)
            if not media or not isinstance(media.get("views"), (int, float)):
                continue
            timestamp = media.get("timestamp")
            if not timestamp:
                continue
            try:
                age = (captured - parse_time(timestamp)).total_seconds() / 3600
            except (ValueError, TypeError):
                continue
            if 36 <= age <= 72:
                observations.append((abs(age - 48), captured, media))
        if not observations:
            continue
        _, captured, media = min(observations, key=lambda x: (x[0], x[1]))
        views = max(0, int(media["views"]))
        saved = media["saved"] if isinstance(media.get("saved"), (int, float)) else 0
        shares = media["shares"] if isinstance(media.get("shares"), (int, float)) else 0
        # Views remain dominant; saves and shares are meaningful but not guaranteed available.
        quality_score = views + min(views, 15 * max(0, saved) + 12 * max(0, shares))
        samples.append({"topic": title, "category": category_of(title),
                        "views_48h": views, "quality_score": quality_score,
                        "media_id": media_id, "sample_at": captured.isoformat(),
                        "slot": marker.get("slot"), "style": marker.get("style")})
    return samples


def optimize():
    samples = load_records()
    categories = defaultdict(list)
    for sample in samples:
        categories[sample["category"]].append(sample["quality_score"])
    enabled = (len(samples) >= MIN_POSTS and
               sum(len(x) >= MIN_PER_CATEGORY for x in categories.values()) >= 3)
    overall = statistics.median(x["quality_score"] for x in samples) if samples else 0
    weights = {}
    for name in (*[name for name, _ in CATEGORY_PATTERNS], "仕事の効率化"):
        scores = categories.get(name, [])
        if enabled and len(scores) >= MIN_PER_CATEGORY:
            median = statistics.median(scores)
            ratio = ((median + 15) / (overall + 15)) ** 0.35
            weights[name] = round(max(MIN_WEIGHT, min(MAX_WEIGHT, ratio)), 3)
        else:
            weights[name] = 1.0
    summary = {
        "updated_at": datetime.now(JST).isoformat(),
        "enabled": enabled,
        "minimum_posts": MIN_POSTS,
        "samples_36_to_72h": len(samples),
        "reason": ("Sufficient comparable Instagram views data"
                   if enabled else "Collect >=30 comparable 48h post samples across >=3 categories"),
        "category_weights": weights,
        "category_samples": {k: len(v) for k, v in categories.items()},
        "method": "48h views + capped, where available, saves/shares; median category scores",
        "observed_first": min((x["sample_at"] for x in samples), default=None),
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print("Optimizer enabled:", enabled, "samples:", len(samples))
    print("Categories:", summary["category_samples"])
    print("Weights:", weights)
    return summary


if __name__ == "__main__":
    optimize()
