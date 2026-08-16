"""Regression tests for PDF report generation.

Audit B3: violation strings were interpolated into ReportLab
Paragraph XML without escaping. In reportlab 4.x this does not crash
the build — it silently corrupts the rendered text: a bare '&' in a
query string gets eaten by the parser's entity scanning (the URL
"v=abc123&format=mp4" renders as "v=abc123&format;=mp4"), and '<' '>'
in LLM text is parsed as markup ("<b>bold</b>" renders as bold with
the tags stripped). These tests extract the PDF text and assert it is
exact, so either corruption mode is caught.
"""
import os

from pypdf import PdfReader

from services.report_generator import generate_report

ASSET = {
    "asset_id": "asset-abc123",
    "original_filename": "poster.jpg",
    "sport": "cricket",
    "team": "Mumbai Indians",
    "event": "World Cup Final",
    "owner": "user-a",
    "uploaded_at": "2026-08-01T00:00:00Z",
}


def _violation(**overrides):
    v = {
        "page_url": "https://example.com/watch?v=abc123&format=mp4&quality=hd",
        "image_url": "https://cdn.example.com/img.jpg?w=1200&h=675&t=9",
        "clip_similarity": 0.95,
        "detected_at": "2026-08-16T10:00:00Z",
        "severity": "HIGH",
        "confidence": 95.0,
        # LLM output is untrusted text: quotes, angle brackets, ampersands
        "explanation": "Law Violated:\nDMCA \u00a7512 & Indian Copyright Act \u2014 'obvious' reuse <512(c)>.",
        "recommended_action": "File a DMCA takedown & notify legal now.",
    }
    v.update(overrides)
    return v


def _extract_text(path: str) -> str:
    return PdfReader(path).pages[0].extract_text() or ""


def test_report_preserves_ampersands_in_urls(tmp_path):
    path = generate_report(ASSET, [_violation()], "TESTRPT1", output_dir=str(tmp_path))
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read(5) == b"%PDF-"
    text = _extract_text(path)
    # Exact URLs, no entity-scan corruption
    assert "https://example.com/watch?v=abc123&format=mp4&quality=hd" in text
    assert "https://cdn.example.com/img.jpg?w=1200&h=675&t=9" in text
    assert "&format;" not in text and "&h;" not in text


def test_report_preserves_xml_characters_in_llm_text(tmp_path):
    path = generate_report(
        ASSET,
        [_violation(explanation="A <b>bold</b> claim & a 'quote' \u2014 done."),
         _violation(severity="LOW", page_url="https://ok.example.com")],
        "TESTRPT2",
        output_dir=str(tmp_path),
    )
    assert os.path.exists(path)
    text = _extract_text(path)
    # Angle brackets must render literally, not be parsed as markup
    assert "<b>bold</b>" in text
    assert "& a 'quote'" in text


def test_report_generates_with_empty_violations(tmp_path):
    path = generate_report(ASSET, [], "TESTRPT3", output_dir=str(tmp_path))
    assert os.path.exists(path)


def test_report_generates_with_missing_optional_fields(tmp_path):
    path = generate_report(
        ASSET,
        [{"page_url": "https://x.example.com?a=1&b=2"}],
        "TESTRPT4",
        output_dir=str(tmp_path),
    )
    assert os.path.exists(path)
    text = _extract_text(path)
    assert "https://x.example.com?a=1&b=2" in text
