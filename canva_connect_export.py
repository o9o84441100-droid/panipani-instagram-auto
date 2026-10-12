"""Official Canva Connect API -> autofilled, Canva-rendered Instagram Reel.

Unattended publishing MUST use a real Canva-generated MP4, not a mockup image,
a share-page screenshot, or our original Pillow renderer.

Requires a separately authorized Canva Connect app, a valid OAuth access token,
and a Canva template with named autofill fields. Neither the ChatGPT Canva
connector token nor its login cookies are available in GitHub Actions.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlparse

import requests

BASE = "https://api.canva.com/rest/v1"
DESIGN_PATTERN = re.compile(r"^D[A-Za-z0-9_-]{10}$")
FIELDS = ("HOOK", "SITUATION", "PROMPT", "CAUTION", "CTA")


class CanvaAuthorizationRequired(RuntimeError):
    pass


def sanitize_error(response):
    """Never leak a token, request URL, or response JSON from Canva."""
    return f"Canva Connect API returned HTTP {response.status_code}."


class Client:
    def __init__(self, token):
        if not token:
            raise CanvaAuthorizationRequired(
                "Missing Canva Connect OAuth access token. Canva-only publishing is paused."
            )
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }

    def req(self, method, resource, payload=None):
        if not resource.startswith("/"):
            raise ValueError("Relative Canva API path required")
        r = requests.request(method, BASE + resource, headers=self.headers,
                             json=payload, timeout=35)
        if not r.ok:
            raise RuntimeError(sanitize_error(r))
        try:
            return r.json()
        except ValueError as exc:
            raise RuntimeError("Invalid JSON response from Canva Connect API") from exc

    def poll(self, path, max_wait=240):
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            out = self.req("GET", path)
            job = out.get("job") or {}
            status = job.get("status")
            if status == "success":
                return job.get("result") or {}
            if status in ("failed", "error"):
                raise RuntimeError("Canva job failed; no Instagram publish attempted")
            time.sleep(5)
        raise TimeoutError("Canva job did not complete; no Instagram publish attempted")

    def validate_template(self, template_id):
        if not DESIGN_PATTERN.fullmatch(template_id):
            raise ValueError("Invalid Canva design ID")
        out = self.req("GET", f"/designs/{template_id}/dataset")
        dataset = out.get("dataset") or {}
        missing = [x for x in FIELDS
                   if (dataset.get(x) or {}).get("type") != "text"]
        if missing:
            raise RuntimeError("Canva template is missing text autofill fields: " +
                               ", ".join(missing))
        return dataset

    def create_for_post(self, design_id, title, situation, prompt, warning):
        self.validate_template(design_id)
        values = {
            "HOOK": situation,
            "SITUATION": title,
            "PROMPT": prompt,
            "CAUTION": warning,
            "CTA": "保存して、あとで試してみよう",
        }
        payload = {
            "type": "create_from_design",
            "design_id": design_id,
            "title": f"Panipani | {title}",
            "data": {key: {"type": "text", "text": value}
                     for key, value in values.items()},
        }
        created = self.req("POST", "/autofills", payload)
        job_id = (created.get("job") or {}).get("id")
        if not job_id:
            raise RuntimeError("No Canva autofill job ID returned")
        result = self.poll("/autofills/" + job_id)
        design = result.get("design") or {}
        new_id = design.get("id")
        if not isinstance(new_id, str) or not DESIGN_PATTERN.fullmatch(new_id):
            raise RuntimeError("Canva autofill did not return a real design ID")
        return new_id

    def export_video(self, design_id):
        created = self.req("POST", "/exports", {
            "design_id": design_id,
            "format": {"type": "mp4", "quality": "vertical_1080p"},
        })
        job_id = (created.get("job") or {}).get("id")
        if not job_id:
            raise RuntimeError("No Canva export job ID returned")
        result = self.poll("/exports/" + job_id)
        urls = result.get("urls") or []
        if len(urls) != 1:
            raise RuntimeError("Canva must return exactly one MP4 download URL")
        url = urls[0]
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username:
            raise RuntimeError("Canva media must have a secure HTTPS download URL")
        return job_id, url


def download_mp4(url, filename):
    dest = Path(filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".downloading")
    try:
        with requests.get(url, timeout=(15, 65), stream=True) as r:
            if not r.ok:
                raise RuntimeError(f"Canva export download failed: HTTP {r.status_code}")
            if not r.url.startswith("https://"):
                raise RuntimeError("Canva export redirected to insecure media")
            size = 0
            with tmp.open("wb") as target:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    if chunk:
                        size += len(chunk)
                        if size > 150_000_000:
                            raise RuntimeError("Canva MP4 exceeds 150 MB safety limit")
                        target.write(chunk)
        if size < 20_000 or b"ftyp" not in tmp.read_bytes()[:64]:
            raise RuntimeError("Downloaded Canva media is not a valid MP4 container")
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return dest


def verify_video(filename):
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(filename)],
        timeout=30,
    )
    data = json.loads(raw)
    video = next((x for x in data.get("streams", []) if x.get("codec_type") == "video"), None)
    if not video or video.get("width") != 1080 or video.get("height") != 1920:
        raise RuntimeError("Canva MP4 must be 1080x1920 for Reels")
    duration = float((data.get("format") or {}).get("duration") or 0)
    if not (3 <= duration <= 90):
        raise RuntimeError("Canva Reel duration must be 3-90 seconds")
    if video.get("codec_name") != "h264":
        raise RuntimeError("Canva MP4 must use H.264 video")
    return data


def write_provenance(filename, template_id, design_id, export_id):
    data = {
        "source": "canva_connect_api",
        "source_template_id": template_id,
        "canva_design_id": design_id,
        "canva_export_job_id": export_id,
        "video_file": str(filename),
        "video_sha256": hashlib.sha256(Path(filename).read_bytes()).hexdigest(),
    }
    Path("output").mkdir(exist_ok=True)
    Path("output/canva_provenance.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def main():
    import daily_reel
    info = daily_reel.context()
    if daily_reel.state_file(info).exists():
        raise RuntimeError("This slot has already been published")
    ids = [x.strip() for x in os.getenv("CANVA_TEMPLATE_IDS", "").split(",") if x.strip()]
    if not ids:
        raise CanvaAuthorizationRequired("No approved Canva autofill templates configured")
    selected = ids[int(hashlib.sha256(info["key"].encode()).hexdigest(), 16) % len(ids)]
    token = os.getenv("CANVA_ACCESS_TOKEN", "")
    client = Client(token)
    title, situation, prompt, warning = info["topic"]
    print("Canva-only Reel:", info["key"], "template:", selected)
    new_design = client.create_for_post(selected, title, situation, prompt, warning)
    export_id, url = client.export_video(new_design)
    filename = "panipani-" + info["key"].replace("-", "") + ".mp4"
    dest = download_mp4(url, Path("site/reels") / filename)
    verify_video(dest)
    write_provenance(dest, selected, new_design, export_id)
    Path("output/filename.txt").write_text(filename, encoding="utf-8")
    Path("output/caption.txt").write_text(
        f"【AI活用Tips】{title}\n\nこんな時に：{situation}\n\n"
        f"▼ 使えるプロンプト\n{prompt}\n\n"
        f"確認ポイント：{warning}\n\n"
        "#AI活用 #ChatGPT活用 #仕事効率化 #Panipani",
        encoding="utf-8")
    Path("site/index.html").write_text(
        "<!doctype html><html lang='ja'><title>Panipani</title>"
        "<meta name='robots' content='noindex'><body>Video delivery</body></html>",
        encoding="utf-8")
    print("Canva media validated, prepared:", filename, "design:", new_design)


if __name__ == "__main__":
    main()
