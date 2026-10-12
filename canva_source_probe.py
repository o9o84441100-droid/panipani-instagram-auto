"""Check whether Canva's *public share pages* expose export-quality graphics.

This is a read-only capability probe; it never uses credentials and never posts.
Canva's authenticated export API is not exposed by the connected ChatGPT tool.
"""
import json
import re
import sys
from urllib.parse import urlsplit
import requests
from html.parser import HTMLParser

PAGES = [
    ("ai_tips", "https://www.canva.com/d/njLf_4_ivByEHgN"),
    ("before_after", "https://www.canva.com/d/xsz6It1hGAnDBrz"),
    ("chat_demo", "https://www.canva.com/d/43PAePKQhkOnrQ5"),
]

class OGImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.candidates=[]
    def handle_starttag(self,tag,attrs):
        if tag!="meta": return
        data=dict(attrs)
        if data.get("property") in ("og:image","og:image:url","twitter:image"):
            url=data.get("content","")
            if url.startswith("https://"):
                self.candidates.append(url)

def main():
    results=[]
    for key,url in PAGES:
        record={"design":key,"link":url,"public_html":False,"has_og_image":False}
        try:
            r=requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0 Panipani link preview"},allow_redirects=True)
            record["http_status"]=r.status_code
            record["final_host"]=urlsplit(r.url).hostname
            record["content_type"]=r.headers.get("Content-Type","").split(";")[0]
            if r.status_code==200 and "html" in r.headers.get("Content-Type",""):
                record["public_html"]=True
                parser=OGImages()
                parser.feed(r.text[:2_000_000])
                record["has_og_image"]=bool(parser.candidates)
                # Only report metadata, not URLs with tokens or transient signatures.
                if parser.candidates:
                    im=requests.get(parser.candidates[0],timeout=25)
                    record["preview_status"]=im.status_code
                    record["preview_bytes"]=len(im.content)
                    if im.ok and im.headers.get("Content-Type","").startswith("image/"):
                        from io import BytesIO
                        from PIL import Image
                        with Image.open(BytesIO(im.content)) as image:
                            record["preview_pixels"]=list(image.size)
        except (requests.RequestException,ValueError,OSError) as e:
            record["error_type"]=type(e).__name__
        results.append(record)
    print(json.dumps(results,ensure_ascii=False,indent=2))
    if not any(r.get("preview_pixels",[0,0])[0]>=720 for r in results):
        print("No proven high-resolution unauthenticated Canva export path; Canva-only publishing remains paused.",file=sys.stderr)

if __name__=="__main__":
    main()
