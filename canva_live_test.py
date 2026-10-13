"""Manual, non-publishing live Canva smoke test across approved designs.

This module has no Instagram API calls, no Pages deployment, no scheduler.
Artifacts are available only from the selected GitHub Actions run.
"""
import hashlib
import json
import os
from pathlib import Path

import canva_connect_export as ce
from canva_copy import make_visual_copy, validate_topic_bank
from canva_oauth import get_access_token
from daily_topics import TOPICS

APPROVED = ("DAHX1n4SSpU", "DAHX1rftBb4", "DAHX1vFRj1g")
OUTDIR = Path("canva-test-output")

def main():
    # Check configuration BEFORE consuming Canva's rotating refresh token.
    configured = tuple(x.strip() for x in os.environ.get("CANVA_TEMPLATE_IDS", "").split(",") if x.strip())
    if configured != APPROVED:
        raise RuntimeError("CANVA_TEMPLATE_IDS must match the three approved Canva designs")
    for key in ("CANVA_CLIENT_ID", "CANVA_CLIENT_SECRET", "CANVA_TOKEN_KEY"):
        if not os.environ.get(key):
            raise RuntimeError("Missing required Canva GitHub secret: " + key)
    selected = os.environ.get("CANVA_TEST_TEMPLATE", "all")
    if selected != "all" and selected not in APPROVED:
        raise RuntimeError("Unapproved Canva template selected")
    checked_topics = validate_topic_bank()
    print(f"Validated microcopy for {checked_topics} topics")
    templates = list(APPROVED) if selected == "all" else [selected]
    test_topics = [
        max(TOPICS, key=lambda topic: len(topic[1])),
        max(TOPICS, key=lambda topic: len(make_visual_copy(*topic)["PROMPT"])),
        max(TOPICS, key=lambda topic: len(topic[3])),
    ]
    # Serialize all exports under a SINGLE access token and rotation.
    client = ce.Client(get_access_token())
    print("Canva OAuth refresh and secure token rotation succeeded")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for template in templates:
        topic = test_topics[APPROVED.index(template)]
        values = make_visual_copy(*topic)
        print("Validating Canva template:", template, "topic:", topic[0],
              "lengths:", {k: len(v) for k,v in values.items()})
        new_design = client.create_for_post(template, *topic)
        job, media_url = client.export_video(new_design)
        output = OUTDIR / (template + ".mp4")
        ce.download_mp4(media_url, output)
        ce.normalize_audio(output)
        video_info = ce.verify_video(output)
        rows.append({
            "template": template,
            "title": topic[0],
            "new_design": new_design,
            "canva_export_job": job,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "video_file": output.name,
            "video_bytes": output.stat().st_size,
            "duration_seconds": float(video_info["format"]["duration"]),
            "visual_copy": values,
        })
        print("SUCCESS: authentic Canva MP4:", template, "bytes:", output.stat().st_size)
    (OUTDIR / "manifest.json").write_text(
        json.dumps({"status": "PASS_CANVA_ONLY_NO_INSTAGRAM_PUBLICATION",
                    "results": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"PASS: {len(rows)} Canva templates rendered, validated and archived.")
    print("Never contacted Instagram. No public posting occurred.")

if __name__ == "__main__":
    main()
