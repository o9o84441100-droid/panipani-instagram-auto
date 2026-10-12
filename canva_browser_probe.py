"""Test rendering Canva's already shared view page, without any Canva credentials."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

SOURCES=[
 ("ai_tips", "https://www.canva.com/d/njLf_4_ivByEHgN"),
 ("before_after", "https://www.canva.com/d/xsz6It1hGAnDBrz"),
 ("chat_demo", "https://www.canva.com/d/43PAePKQhkOnrQ5"),
]

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    page=browser.new_page(viewport={"width":1080,"height":1920}, device_scale_factor=1)
    for name,url in SOURCES:
        try:
            resp=page.goto(url,wait_until="domcontentloaded",timeout=30000)
            page.wait_for_timeout(3500)
            location=page.url
            title=page.title()
            body=page.locator("body").inner_text(timeout=6000)[:300]
            screenshot_path=f"output/canva-view-{name}.png"
            Path("output").mkdir(exist_ok=True)
            page.screenshot(path=screenshot_path,full_page=False,timeout=10000)
            from PIL import Image, ImageStat
            im=Image.open(screenshot_path).convert("RGB")
            stats=ImageStat.Stat(im)
            print(json.dumps({
              "source":name,"http":resp.status if resp else None,
              "page_title":title[:120],
              "final_host":location.split("/")[2],
              "body_text_prefix":body[:180],
              "screenshot_size":im.size,
              "png_bytes":os.path.getsize(screenshot_path),
              "rgb_stddev":[round(x,2) for x in stats.stddev]
            },ensure_ascii=False))
        except Exception as exc:
            print(json.dumps({"source":name,"error":type(exc).__name__,"detail":str(exc)[:170]}))
    browser.close()
