"""Instagram Login API: validate connection; publish only when explicitly enabled."""
import os, sys, json, time
import requests

API = "https://graph.instagram.com"
IG_ID = os.getenv("INSTAGRAM_USER_ID", "28854255504200287")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
MODE = os.getenv("PUBLISH_MODE", "check")
VIDEO_URL = os.getenv("VIDEO_URL", "")
CAPTION = os.getenv("CAPTION", "Panipani | AI活用のヒント")

def call(method, path, **kwargs):
    r = requests.request(method, API + path, timeout=45, **kwargs)
    try:
        data = r.json()
    except ValueError:
        raise RuntimeError(f"API returned HTTP {r.status_code}, non-JSON response")
    if not r.ok or "error" in data:
        error = data.get("error", {})
        raise RuntimeError(f"Instagram API HTTP {r.status_code}: {error.get('message', 'unknown error')} (code={error.get('code', '?')})")
    return data

def main():
    if not TOKEN:
        print("INSTAGRAM_ACCESS_TOKEN secret is not configured; no API call made.")
        return 0
    headers = {"Authorization": f"Bearer {TOKEN}"}
    me = call("GET", "/me", headers=headers, params={"fields": "id,username"})
    if str(me.get("id")) != IG_ID:
        raise RuntimeError("Instagram account ID mismatch. Publishing blocked.")
    print("Connected account:", me.get("username"))
    quota = call("GET", f"/{IG_ID}/content_publishing_limit", headers=headers)
    print("Publishing quota usage:", quota.get("data", [{}])[0].get("quota_usage", "unknown"))
    if MODE != "publish":
        print("CHECK ONLY: no media container created, no post published.")
        return 0
    if not VIDEO_URL.startswith("https://"):
        raise RuntimeError("VIDEO_URL must be a publicly fetchable HTTPS MP4 URL.")
    if os.getenv("CONFIRM_PUBLICATION") != "YES":
        raise RuntimeError("Publication disabled: CONFIRM_PUBLICATION must equal YES.")
    created = call("POST", f"/{IG_ID}/media", headers=headers, data={
        "media_type": "REELS", "video_url": VIDEO_URL, "caption": CAPTION
    })
    container = created["id"]
    print("Container created:", container)
    for _ in range(30):
        status = call("GET", f"/{container}", headers=headers, params={"fields": "status_code"})
        code = status.get("status_code")
        print("Container status:", code)
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError("Instagram processing failed: " + code)
        time.sleep(20)
    else:
        raise RuntimeError("Container processing timed out; publication not attempted.")
    published = call("POST", f"/{IG_ID}/media_publish", headers=headers, data={"creation_id": container})
    print("Published media ID:", published.get("id"))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("FAILED:", str(exc), file=sys.stderr)
        sys.exit(1)
