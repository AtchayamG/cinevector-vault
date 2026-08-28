import json
from pathlib import Path


def test_track2_cinematic_evidence_manifest_and_docs():
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = repo_root / "docs" / "evidence" / "cinematic_evidence_manifest.json"
    evidence_md = repo_root / "docs" / "evidence" / "CINEMATIC_EVIDENCE.md"
    thumbnail = repo_root / "docs" / "assets" / "cinematic-evidence-thumbnail.jpg"
    ip_review = repo_root / "docs" / "evidence" / "TRACK2_IP_RESEMBLANCE_REVIEW.md"
    ip_plan = repo_root / "docs" / "evidence" / "TRACK2_IP_REMEDIATION_PLAN.md"

    assert manifest_path.exists(), "Manifest must exist in repo docs/evidence"
    assert evidence_md.exists(), "CINEMATIC_EVIDENCE.md must exist"
    assert thumbnail.exists(), "Thumbnail must exist in docs/assets"
    assert thumbnail.stat().st_size > 10000, "Thumbnail must be valid image"
    assert ip_review.exists(), "IP review must exist"
    assert ip_plan.exists(), "IP remediation plan must exist"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["evidence_type"] == "supplemental_pregenerated_cinematic_evidence"
    assert manifest["track_number"] == 2
    assert manifest["model"] == "veo-3.1-fast-generate-001"
    assert manifest["total_shots"] == 7
    assert manifest["total_duration_seconds"] == 56.03
    assert manifest["master_sha256"] == "df66d91f230c58ac31c0295cbb8d2a803a75328b38216a58fadac566f66ea05d"
    assert "Supplemental pre-generated cinematic evidence" in manifest["truthful_disclaimer"]

    content = evidence_md.read_text(encoding="utf-8")
    assert "veo-3.1-fast-generate-001" in content
    assert "df66d91f230c58ac31c0295cbb8d2a803a75328b38216a58fadac566f66ea05d" in content
    assert "No Raw Frame Ingestion" in content
    assert "ClickHouse indexes structured metadata" in content

    review_text = ip_review.read_text(encoding="utf-8")
    assert "BLOCKED FOR PUBLICATION" in review_text
