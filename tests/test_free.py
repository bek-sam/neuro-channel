"""Offline tests for code/free: no network, no keys.   .venv/bin/python -m pytest tests -q"""
import os, sys, json
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [f"{ROOT}/code", f"{ROOT}/code/gpu"]
os.environ.setdefault("HF_REPO", "test/repo")
from free import providers as pv  # noqa: E402


@pytest.fixture
def ledger(monkeypatch):
    """In-memory budget ledger instead of the HF dataset file."""
    led = {}
    monkeypatch.setattr(pv, "_ledger", lambda: dict(led))
    monkeypatch.setattr(pv, "budget_spend", lambda who, usd: led.__setitem__(who, round(led.get(who, 0) + usd, 4)))
    return led


def test_kaggle_slug_per_project():
    from free.run import kaggle_base
    assert kaggle_base("dopamine-scroll") == "vg-dopamine-scroll"
    assert kaggle_base("a_b__c") == "vg-a-b-c"
    long = kaggle_base("x" * 61) + "-heroes"
    assert 5 <= len(long) <= 50
    assert kaggle_base("dopamine-scroll") != kaggle_base("sleep-video")


def test_budget_left(ledger, monkeypatch):
    monkeypatch.setitem(pv.CAPS, "muapi", 5.0)
    ledger["muapi"] = 4.5
    assert pv.budget_left("muapi") == pytest.approx(0.5)


def test_muapi_over_cap_is_quota(ledger, monkeypatch, tmp_path):
    monkeypatch.setitem(pv.CAPS, "muapi", 1.0); ledger["muapi"] = 0.9
    monkeypatch.setenv("MUAPI_API_KEY", "k")
    img = tmp_path / "a.png"; img.write_bytes(b"png")
    with pytest.raises(pv.QuotaError): pv.Muapi().clip(str(img), "p", 1, str(tmp_path / "o.mp4"))


def test_muapi_payload_fields(monkeypatch):
    m = pv.Muapi()
    m.MODEL = "kling-v2.5-turbo-std-i2v"; p = m.payload("U", "go")
    assert p == {"prompt": "go", "image_url": "U", "duration": 5}
    m.MODEL = "seedance-2-mini-image-to-video"; p = m.payload("U", "go")
    assert p["images_list"] == ["U"] and "image_url" not in p
    m.MODEL = "veo3.1-lite-image-to-video"; p = m.payload("U", "go")
    assert "duration" not in p and p["image_url"] == "U"


def test_muapi_flow(ledger, monkeypatch, tmp_path):
    """upload -> submit -> poll (processing, then completed with a reported cost) -> download; cost goes in the ledger."""
    import httpx
    monkeypatch.setenv("MUAPI_API_KEY", "k"); monkeypatch.setitem(pv.CAPS, "muapi", 5.0)
    monkeypatch.setattr(pv.time, "sleep", lambda s: None)
    polls, seen = iter([{"status": "processing"}, {"status": "completed", "outputs": ["https://cdn.example/v.mp4"],
                                                    "cost": {"amount_usd": 0.28}}]), []
    def handler(req):
        seen.append((req.method, req.url.path)); assert req.headers["x-api-key"] == "k"
        if req.url.path.endswith("/upload_file"): return httpx.Response(200, json={"url": "https://cdn.example/a.png"})
        if req.url.path.endswith("/kling-v2.5-turbo-std-i2v"):
            assert json.loads(req.content)["image_url"] == "https://cdn.example/a.png"
            return httpx.Response(200, json={"request_id": "r1"})
        if "/predictions/r1/result" in req.url.path: return httpx.Response(200, json=next(polls))
        if req.url.host == "cdn.example": return httpx.Response(200, content=b"MP4DATA")
        return httpx.Response(404)
    m = pv.Muapi(); m.MODEL = "kling-v2.5-turbo-std-i2v"
    monkeypatch.setattr(m, "_http", lambda: httpx.Client(base_url=m.BASE, headers={"x-api-key": "k"}, transport=httpx.MockTransport(handler)))
    img = tmp_path / "a.png"; img.write_bytes(b"png"); out = tmp_path / "o.mp4"
    m.clip(str(img), "slow push in", 3, str(out))
    assert out.read_bytes() == b"MP4DATA"
    assert ledger["muapi"] == pytest.approx(0.28)
    assert [p for _, p in seen].count("/api/v1/predictions/r1/result") == 2


def test_muapi_402_is_quota(ledger, monkeypatch, tmp_path):
    import httpx
    monkeypatch.setenv("MUAPI_API_KEY", "k"); monkeypatch.setitem(pv.CAPS, "muapi", 5.0)
    m = pv.Muapi()
    monkeypatch.setattr(m, "_http", lambda: httpx.Client(base_url=m.BASE, transport=httpx.MockTransport(
        lambda req: httpx.Response(402, json={"detail": "Insufficient balance"}))))
    img = tmp_path / "a.png"; img.write_bytes(b"png")
    with pytest.raises(pv.QuotaError): m.clip(str(img), "p", 1, str(tmp_path / "o.mp4"))
    assert "muapi" not in ledger  # nothing was submitted, nothing counted


def test_modal_over_cap_is_quota(ledger, monkeypatch, tmp_path):
    monkeypatch.setitem(pv.CAPS, "modal", 25.0); ledger["modal"] = 24.9
    with pytest.raises(pv.QuotaError): pv.ModalWan().clip("x.png", "p", 1, str(tmp_path / "o.mp4"))


def test_video_order_free_first():
    names = [p.name for p in pv.VIDEO]
    assert names[:3] == ["zg_wan22", "zg_wan22_r3gm", "zg_ltx23"] and names[-2:] == ["modal_wan22", "muapi"]


def test_router_falls_through_on_quota(monkeypatch):
    from free.run import Router
    class P:
        def __init__(s, name, exc=None): s.name, s.kind, s.quality, s.limit, s.exc, s.calls = name, "video", 8, 1, exc, 0
        def available(s): return True
        def clip(s, *a):
            s.calls += 1
            if s.exc: raise s.exc
    monkeypatch.setattr("free.run.time.sleep", lambda s: None)
    a, b = P("free", pv.QuotaError("out")), P("paid")
    r = Router([a, b], lambda *x, **k: None)
    assert r.run("clip", "clip 0") == "paid" and r.run("clip", "clip 1") == "paid"
    assert a.calls == 1 and b.calls == 2  # the free one is skipped after its quota error
