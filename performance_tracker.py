"""Read-only Instagram metrics collector for Panipani.
Stores only non-secret, public-account-scale aggregates and media metrics.
Does not manufacture unavailable reach/views or bypass permission requirements.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

ROOT = Path("state/analytics")
SUMMARY = Path("performance_report.md")
IG_ID = os.getenv("INSTAGRAM_USER_ID", "28854255504200287")
BASE = "https://graph.instagram.com"
JST = ZoneInfo("Asia/Tokyo")
NOW = datetime.now(JST)
DAY = NOW.date().isoformat()
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
HEADERS = {"Authorization": "Bearer " + TOKEN}
ERRORS = []


def call(path, params=None, required=False):
    try:
        r = requests.get(BASE + path, params=params or {}, headers=HEADERS,
                         timeout=30)
        try:
            data = r.json()
        except ValueError:
            data = {}
        if not r.ok or data.get("error"):
            err = data.get("error") or {}
            code = err.get("code", r.status_code)
            msg = str(err.get("message", "Request failed"))
            # Never print token, URLs containing credentials, or raw responses.
            reason = "HTTP " + str(r.status_code) + ", code=" + str(code)
            if "permission" in msg.lower() or code in (10, 200):
                reason += " (additional Instagram Insights permission may be required)"
            if required:
                raise RuntimeError("Instagram API call failed: " + reason)
            ERRORS.append(path.rsplit("/", 1)[-1] + " " + reason)
            return None, r.status_code, code
        return data, r.status_code, None
    except requests.RequestException as exc:
        if required:
            raise RuntimeError("Instagram API connection error: " +
                               type(exc).__name__) from exc
        ERRORS.append("network: " + type(exc).__name__)
        return None, 0, None


def account_snapshot():
    data, status, code = call("/me", {"fields": "id,username,followers_count,media_count"})
    if data is None:
        data, _, _ = call("/me", {"fields": "id,username"}, required=True)
    if str(data.get("id")) != IG_ID:
        raise RuntimeError("Connected Instagram account differs from expected account")
    return {
        "id": IG_ID,
        "username": data.get("username"),
        "followers": data.get("followers_count"),
        "media_count": data.get("media_count"),
    }


def collect_media():
    # Instagram Login allows these metadata fields with basic permissions.
    fields = "id,caption,permalink,media_type,timestamp,like_count,comments_count"
    params = {"fields": fields, "limit": 50}
    result, status, code = call("/" + IG_ID + "/media", params)
    if result is None:
        result, status, code = call("/" + IG_ID + "/media",
                                  {"fields": "id,caption,media_type,timestamp",
                                   "limit": 50}, required=True)
    result = result or {}
    cutoff = NOW - timedelta(days=18)
    posts = []
    for media in (result.get("data") or []):
        if len(posts) >= 50:
            break
        stamp = media.get("timestamp")
        if stamp:
            try:
                posted = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                if posted < cutoff:
                    continue
            except ValueError:
                pass
        posts.append({
            "id": str(media.get("id", "")),
            "timestamp": stamp,
            "media_type": media.get("media_type"),
            "permalink": media.get("permalink"),
            "likes": media.get("like_count"),
            "comments": media.get("comments_count"),
            "caption_start": (media.get("caption") or "")[:120],
            "views": None,
            "reach": None,
            "saved": None,
            "shares": None,
        })
    return posts


def numeric_metric(metric):
    # Meta can return values[0].value or total_value.value.
    raw = metric.get("total_value")
    if isinstance(raw, dict):
        raw = raw.get("value")
    if raw is None:
        values = metric.get("values") or []
        raw = values[0].get("value") if values else None
    return raw if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None


def collect_insights(posts):
    available = False
    note = "Not requested"
    for index, media in enumerate(posts[:30]):
        if not media["id"]:
            continue
        data, status, code = call("/" + media["id"] + "/insights",
                                  {"metric": "views,reach,saved,shares"})
        if data is None:
            if status in (400, 401, 403) or code in (10, 100, 190, 200):
                note = ("Media Insights unavailable: verify "
                        "instagram_business_manage_insights permission in Meta app "
                        "and issue a token with that permission.")
                break
            note = "Some media insights unavailable; review API status."
            continue
        available = True
        note = "Media Insights available"
        for metric in (data.get("data") or []):
            name = metric.get("name")
            if name in ("views", "reach", "saved", "shares"):
                media[name] = numeric_metric(metric)
    return {"available": available, "note": note}


def load_previous():
    for file in sorted(ROOT.glob("????-??-??.json"), reverse=True):
        if file.stem >= DAY:
            continue
        try:
            return json.loads(file.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
    return None


def row_metric(post, name):
    v = post.get(name)
    return str(v) if isinstance(v, (int, float)) else "取得不可"


def make_report(snapshot, previous):
    a = snapshot["account"]
    followers = a.get("followers")
    earlier = (previous or {}).get("account", {}).get("followers")
    delta = (followers - earlier) if isinstance(followers, int) and isinstance(earlier, int) else None
    lines = [
        "# Panipani Instagram 日次パフォーマンス",
        "",
        "集計日: " + DAY + "（JST）",
        "アカウント: @" + str(a["username"]),
        "フォロワー: " + (str(followers) if isinstance(followers, int) else "取得不可"),
        "前回記録との差: " + (f"{delta:+d}" if delta is not None else "比較不可"),
        "",
        "インサイト: " + snapshot["insights"]["note"],
        "",
        "## 最近の投稿（取得できた範囲）",
        "| 投稿日時 | テーマ（キャプション冒頭） | 閲覧 | リーチ | いいね | コメント | 保存 | シェア |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    posts = snapshot["posts"][:20]
    for post in posts:
        title = (post["caption_start"].splitlines() or [""])[0]
        title = title.replace("|", "／").replace("\n", " ")
        lines.append("| " + " | ".join([
            str(post.get("timestamp") or "不明")[:16],
            title[:45],
            *[row_metric(post, x) for x in ("views", "reach", "likes", "comments", "saved", "shares")]
        ]) + " |")
    if not posts:
        lines.append("| - | 投稿が見つかりません | - | - | - | - | - | - |")
    lines += ["", "## 判断",
              "- 再生数・保存数・フォロー増加など、取得できない項目はゼロとして扱わない。",
              "- 再生数が取れる場合も、投稿から48時間未満のリールは過去投稿と単純比較しない。",
              "- 1〜2日程度の単発結果で投稿時間を頻繁に変えず、最低14日単位で検証する。",
              "- 具体的な改善は、取得できた指標・十分な投稿数を確認して行う。",
              "",
              "## 取得・投稿障害",
              *(["- " + error for error in snapshot["errors"][:10]]
                if snapshot["errors"] else ["- 今回取得時に記録されたAPIエラーなし"]),
              "",
              "GitHub実行履歴: https://github.com/o9o84441100-droid/panipani-instagram-auto/actions",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if not TOKEN:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN secret not set")
    a = account_snapshot()
    posts = collect_media()
    insights = collect_insights(posts)
    previous = load_previous()
    snapshot = {
        "date": DAY,
        "checked_at": NOW.isoformat(),
        "account": a,
        "insights": insights,
        "post_count_fetched": len(posts),
        "posts": posts,
        "errors": ERRORS[:20],
    }
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / (DAY + ".json")).write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    make_report(snapshot, previous)
    print("Instagram account:", a["username"])
    print("Followers:", a.get("followers"), "Recent media:", len(posts))
    print("Insights availability:", insights["note"])
    print("Saved snapshot:", ROOT / (DAY + ".json"))
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as out:
            out.write(SUMMARY.read_text(encoding="utf-8"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Performance collection FAILED:", str(exc), file=sys.stderr)
        raise
