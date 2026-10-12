"""Offline Canva-only policy and Canva Connect request-contract checks."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import canva_connect_export as ce
import publisher


class MockResponse:
    def __init__(self, value, status=200):
        self.payload=value
        self.status_code=status
        self.ok=200 <= status < 300
    def json(self):
        return self.payload


class CanvaConnectTests(unittest.TestCase):
    def test_unconnected_canva_cannot_export(self):
        with self.assertRaises(ce.CanvaAuthorizationRequired):
            ce.Client("")
    def test_missing_autofill_fields_block(self):
        with patch("requests.request", return_value=MockResponse({"dataset":{}})):
            with self.assertRaisesRegex(RuntimeError, "HOOK"):
                ce.Client("redacted-test-token").validate_template("DAHX1n4SSpU")

    def test_official_autofill_then_mp4_export(self):
        calls=[]
        values={
            "dataset": {k: {"type":"text"} for k in ce.FIELDS},
            "autofills_job": {"job":{"id":"autofill-job"}},
            "autofills_result":{"job":{"status":"success","result":{"design":{"id":"DAHX1vFRj1g"}}}},
            "exports_job":{"job":{"id":"export-job"}},
            "exports_result":{"job":{"status":"success","result":{
                "urls":["https://export-download.canva.com/test.mp4"]}}},
        }
        def send(method,url,**kwargs):
            calls.append((method,url,kwargs.get("json")))
            if method=="GET" and url.endswith("/dataset"):
                return MockResponse({"dataset": values["dataset"]})
            if method=="POST" and url.endswith("/autofills"):
                return MockResponse(values["autofills_job"])
            if method=="GET" and "/autofills/" in url:
                return MockResponse(values["autofills_result"])
            if method=="POST" and url.endswith("/exports"):
                return MockResponse(values["exports_job"])
            if method=="GET" and "/exports/" in url:
                return MockResponse(values["exports_result"])
            raise AssertionError("Unexpected URL: " + url)
        with patch("requests.request",side_effect=send):
            client=ce.Client("redacted-test-token")
            item=client.create_for_post("DAHX1n4SSpU","メール返信","どう書く？",
                                        "丁寧な150字の返信を作る","送る前に確認")
            export_id,download=client.export_video(item)
        self.assertEqual(item,"DAHX1vFRj1g")
        self.assertEqual(export_id,"export-job")
        self.assertTrue(download.startswith("https://export-download.canva.com/"))
        fill=next(p for m,u,p in calls if u.endswith("/autofills"))
        self.assertEqual(fill["type"],"create_from_design")
        self.assertEqual(set(fill["data"]),set(ce.FIELDS))
        video=next(p for m,u,p in calls if u.endswith("/exports"))
        self.assertEqual(video["format"],{"type":"mp4","quality":"vertical_1080p"})


class CanvaPublisherPolicyTests(unittest.TestCase):
    def setUp(self):
        self.old_dir=Path.cwd()
        self.old_url=publisher.VIDEO_URL
        self.temp=tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
    def tearDown(self):
        publisher.VIDEO_URL=self.old_url
        os.chdir(self.old_dir)
        self.temp.cleanup()

    def test_missing_provenance_blocks_publish(self):
        publisher.VIDEO_URL="https://example.com/reels/test.mp4"
        with self.assertRaisesRegex(RuntimeError,"CANVA-ONLY"):
            publisher.require_canva_provenance()

    def test_fake_or_modified_canva_video_is_blocked(self):
        f=Path("site/reels/test.mp4")
        f.parent.mkdir(parents=True)
        f.write_bytes(b"0000ftyp" + b"dummy-video-test" * 10)
        record={
            "source":"canva_connect_api",
            "source_template_id":"DAHX1n4SSpU",
            "canva_design_id":"DAHX1vFRj1g",
            "canva_export_job_id":"official-export-job",
            "video_file":str(f),
            "video_sha256":hashlib.sha256(f.read_bytes()).hexdigest()
        }
        Path("output").mkdir()
        path=Path("output/canva_provenance.json")
        path.write_text(json.dumps(record),encoding="utf-8")
        publisher.VIDEO_URL="https://example.com/reels/test.mp4"
        publisher.require_canva_provenance()
        f.write_bytes(f.read_bytes()+b"tampered")
        with self.assertRaisesRegex(RuntimeError,"checksum"):
            publisher.require_canva_provenance()
        f.write_bytes(b"0000ftyp" + b"dummy-video-test" * 10)
        record["source"]="canva_inspired"
        path.write_text(json.dumps(record),encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError,"official Canva"):
            publisher.require_canva_provenance()

if __name__=="__main__":
    unittest.main()
