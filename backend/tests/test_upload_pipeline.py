"""Tests for the /upload/asset pipeline (B1: video support + temp/orphan hygiene).

Covered:
1. Successful image upload
2. Successful video upload + CLIP frame-sampling fingerprint
3. Fingerprint failure after Supabase upload => cloud object deleted (no orphans)
   3a. corrupt video (real OpenCV decode failure)
   3b. pgvector upsert failure
4. Temp file lives in OS temp, exists during processing, deleted on success
5. Temp file deleted on failure
"""
import os
import re
import tempfile

import cv2
import numpy as np
import pytest
import torch
from PIL import Image

import services.fingerprint as fingerprint
import routers.upload as upload_mod
from conftest import make_png_bytes

PHASH_RE = re.compile(r"^[0-9a-f]{16}$")
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_video_bytes() -> bytes:
    # Payload is arbitrary for tests that fake VideoCapture;
    # the corrupt-video tests reuse it with the REAL cv2.
    return b"\x00\x01\x02NOT-A-REAL-VIDEO"


# ---------------------------------------------------------------------------
# 1. Successful image upload
# ---------------------------------------------------------------------------

def test_successful_image_upload(
    client, fake_supabase, fake_vector_store, fake_db_insert
):
    resp = client.post(
        "/upload/asset",
        files={"file": ("jersey.png", make_png_bytes(), "image/png")},
        data={
            "sport": "cricket",
            "team": "Mumbai Indians",
            "event": "IPL 2026",
            "description": "Team jersey",
            "date": "2026-01-15",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["asset_id"]
    assert body["filename"].startswith(body["asset_id"])
    assert body["filename"].endswith(".png")
    # Private bucket: clients get short-lived signed URLs, never public ones
    assert "/object/public/" not in body["file_url"]
    assert "token=fake-signature" in body["file_url"]

    fp = body["fingerprint"]
    assert PHASH_RE.match(fp["phash"])
    assert fp["stored_in_db"] is True

    # Exactly one Supabase Storage object, in the "assets" bucket
    assert fake_supabase["bucket"] == "assets"
    assert len(fake_supabase["uploads"]) == 1
    assert fake_supabase["uploads"][0]["path"] == body["filename"]
    assert fake_supabase["removes"] == []

    # Metadata row written for the right owner, with phash + file_url
    assert len(fake_db_insert) == 1
    row = fake_db_insert[0]
    assert row["owner"] == "test-user-123"
    assert row["phash"] == fp["phash"]
    assert row["file_url"] == body["filename"]  # storage path, not a URL

    # Embedding persisted to pgvector
    assert len(fake_vector_store) == 1
    assert fake_vector_store[0]["asset_id"] == body["asset_id"]
    assert fake_vector_store[0]["metadata"]["type"] == "image"


# ---------------------------------------------------------------------------
# 2. Successful video upload + CLIP frame-sampling fingerprint
# ---------------------------------------------------------------------------

class FakeVideoCapture:
    """Stands in for cv2.VideoCapture on a 12-frame, 30fps clip."""

    last = None

    def __init__(self, path):
        self.path = path
        self.pos = 0
        self.seeks = []
        self.released = False
        FakeVideoCapture.last = self

    def isOpened(self):
        return True

    def get(self, prop):
        if prop == cv2.CAP_PROP_FRAME_COUNT:
            return 12
        if prop == cv2.CAP_PROP_FPS:
            return 30
        return 0

    def set(self, prop, value):
        if prop == cv2.CAP_PROP_POS_FRAMES:
            self.pos = int(value)
            self.seeks.append(self.pos)
        return True

    def read(self):
        frame = np.zeros((360, 640, 3), dtype=np.uint8)
        frame[:, :, 0] = self.pos  # deterministic per position
        return True, frame

    def release(self):
        self.released = True


class _Inputs(dict):
    def to(self, device):
        return self


class FakeCLIPProcessor:
    def __call__(self, images, return_tensors="pt"):
        assert isinstance(images, Image.Image), "frames must become PIL images"
        return _Inputs(pixel_values=torch.ones(1, 8))


class FakeCLIPModel:
    def to(self, device):
        return self

    def eval(self):
        return self

    def get_image_features(self, **inputs):
        return torch.ones(1, 8)


def test_successful_video_upload_and_fingerprinting(
    client, fake_supabase, fake_vector_store, fake_db_insert, monkeypatch
):
    monkeypatch.setattr(fingerprint.cv2, "VideoCapture", FakeVideoCapture)
    monkeypatch.setattr(fingerprint, "_clip_model", FakeCLIPModel())
    monkeypatch.setattr(fingerprint, "_clip_processor", FakeCLIPProcessor())

    resp = client.post(
        "/upload/asset",
        files={"file": ("highlight.mp4", make_video_bytes(), "video/mp4")},
        data={"sport": "cricket", "team": "Mumbai Indians", "description": "Match clip"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["filename"].endswith(".mp4")

    fp = body["fingerprint"]
    assert fp["type"] == "video"
    assert fp["frame_count"] == 5  # sampled, not decoded frame-by-frame
    assert PHASH_RE.match(fp["phash"])
    assert fp["stored_in_db"] is True

    # Sampling: seeks into the clip (non-sequential), positions in range
    cap = FakeVideoCapture.last
    assert cap is not None
    assert cap.seeks and len(set(cap.seeks)) >= 2
    assert all(0 <= s <= 11 for s in cap.seeks)
    assert cap.released is True

    # Mean of the 5 identical frame embeddings: raw ones(8) features get
    # L2-normalized to (1/sqrt(8)) per component; averaging + re-normalizing
    # keeps the unit vector.
    assert len(fake_vector_store) == 1
    assert fake_vector_store[0]["embedding"] == pytest.approx(
        [1.0 / (8 ** 0.5)] * 8
    )
    assert fake_vector_store[0]["metadata"]["type"] == "video"

    assert fake_supabase["uploads"][0]["path"] == body["filename"]
    assert fake_supabase["removes"] == []


# ---------------------------------------------------------------------------
# 3. Failure after Supabase upload => cloud object deleted (no orphans)
# ---------------------------------------------------------------------------

def test_corrupt_video_after_storage_upload_deletes_cloud_object(
    client, fake_supabase, fake_vector_store, media_spy
):
    """Real cv2 decode failure after the object is already in storage."""
    resp = client.post(
        "/upload/asset",
        files={"file": ("broken.mp4", make_video_bytes(), "video/mp4")},
        data={"sport": "cricket", "team": "RCB"},
    )
    assert resp.status_code == 400, resp.text
    assert len(fake_supabase["uploads"]) == 1
    # The stored object must be removed again
    assert fake_supabase["removes"] == [[fake_supabase["uploads"][0]["path"]]]


def test_db_upsert_failure_after_storage_upload_deletes_cloud_object(
    client, fake_supabase, fake_vector_store, monkeypatch
):
    """pgvector failure after storage upload must not orphan the object."""
    def boom(asset_id, embedding, metadata, document=""):
        raise RuntimeError("pgvector unavailable")

    monkeypatch.setattr(fingerprint.vector_store, "upsert_asset_embedding", boom)

    resp = client.post(
        "/upload/asset",
        files={"file": ("logo.png", make_png_bytes(), "image/png")},
        data={"sport": "cricket", "team": "RCB"},
    )
    assert resp.status_code == 500, resp.text
    assert len(fake_supabase["uploads"]) == 1
    assert fake_supabase["removes"] == [[fake_supabase["uploads"][0]["path"]]]


# ---------------------------------------------------------------------------
# 4. Temp file: OS temp only, deleted on success
# ---------------------------------------------------------------------------

def test_temp_file_lives_in_system_temp_and_is_deleted_on_success(
    client, media_spy
):
    resp = client.post(
        "/upload/asset",
        files={"file": ("jersey.png", make_png_bytes(), "image/png")},
        data={"sport": "cricket", "team": "Mumbai Indians"},
    )
    assert resp.status_code == 200, resp.text

    path = media_spy.get("path")
    assert path, "fingerprint dispatcher was never called"
    assert media_spy["existed_during_processing"] is True

    # Never inside the project/source tree
    assert not path.lower().startswith(BACKEND_DIR.lower())
    # In the OS temp area
    assert path.lower().startswith(tempfile.gettempdir().lower())

    # Gone after success — file and its temp directory
    assert not os.path.exists(path)
    assert not os.path.exists(os.path.dirname(path))


# ---------------------------------------------------------------------------
# 5. Temp file deleted on failure
# ---------------------------------------------------------------------------

def test_temp_file_deleted_on_failure(client, media_spy):
    resp = client.post(
        "/upload/asset",
        files={"file": ("broken.mp4", make_video_bytes(), "video/mp4")},
        data={"sport": "cricket", "team": "RCB"},
    )
    assert resp.status_code == 400, resp.text

    path = media_spy.get("path")
    assert path, "fingerprint dispatcher was never called"
    assert media_spy["existed_during_processing"] is True
    assert not os.path.exists(path)
    assert not os.path.exists(os.path.dirname(path))


# ---------------------------------------------------------------------------
# 6. Oversized uploads are rejected during streaming (no full buffering)
# ---------------------------------------------------------------------------

def test_oversized_upload_rejected_before_full_buffer(client, monkeypatch, fake_supabase):
    """A body larger than the cap is rejected mid-stream: no storage upload,
    no orphaned temp dirs, generic 400."""
    monkeypatch.setattr(upload_mod, "MAX_SIZE_MB", 1)
    payload = b"\x89PNG\r\n\x1a\n" + b"\x00" * (2 * 1024 * 1024)  # 2MB > 1MB cap

    resp = client.post(
        "/upload/asset",
        files={"file": ("big.png", payload, "image/png")},
        data={"sport": "basketball", "team": "lakers"},
    )

    assert resp.status_code == 400
    assert "too large" in resp.json()["detail"].lower()
    assert fake_supabase["uploads"] == []

    leftovers = [
        d for d in os.listdir(tempfile.gettempdir())
        if d.startswith("sportshield-upload-")
    ]
    assert leftovers == []


# ---------------------------------------------------------------------------
# 7. Streaming uploader aborts mid-transfer on oversized bodies
# ---------------------------------------------------------------------------

class FakeUploadFile:
    """Serves fixed-size chunks; records how many reads were consumed."""

    def __init__(self, chunk: bytes, count: int):
        self._chunk = chunk
        self._remaining = count
        self.read_count = 0

    async def read(self, n=-1):
        if self._remaining <= 0:
            return b""
        self._remaining -= 1
        self.read_count += 1
        return self._chunk


def test_stream_uploader_happy_path(tmp_path):
    import asyncio
    dest = tmp_path / "f.bin"
    up = FakeUploadFile(b"A" * 600_000, 3)
    total = asyncio.run(
        upload_mod.stream_upload_to_disk(up, str(dest), 5 * 1024 * 1024)
    )
    assert total == 1_800_000
    assert dest.read_bytes() == b"A" * 1_800_000


def test_stream_uploader_aborts_without_consuming_all_chunks(tmp_path):
    """A buffered implementation would consume all 10 chunks (6MB) into
    memory before noticing the cap; the streaming one must give up after
    the second chunk crosses 1MB."""
    import asyncio
    dest = tmp_path / "f.bin"
    up = FakeUploadFile(b"B" * 600_000, 10)
    with pytest.raises(upload_mod.FileTooLargeError):
        asyncio.run(
            upload_mod.stream_upload_to_disk(up, str(dest), 1024 * 1024)
        )
    assert up.read_count <= 3, (
        f"read {up.read_count} chunks — implementation is buffering, not streaming"
    )
