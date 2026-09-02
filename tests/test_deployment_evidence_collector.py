from pathlib import Path

import pytest

from aether.deployment.evidence_collector import EvidenceError, collect_evidence
from aether.deployment.lifecycle import create_isolated_root


def test_evidence_rejects_secret_values(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_EVIDENCE", transaction_id="tx_evidence"
    )
    with pytest.raises(EvidenceError):
        collect_evidence(
            root,
            capability=capability,
            facts={"note": "-----BEGIN PRIVATE KEY-----"},
        )
    with pytest.raises(EvidenceError):
        collect_evidence(root, facts={"collector": "test"})


def test_evidence_is_bounded_and_rejects_symlinked_unit_directory(tmp_path: Path):
    root, capability = create_isolated_root(
        tmp_path, purpose="M122A_EVIDENCE", transaction_id="tx_evidence"
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "etc").mkdir()
    (root / "etc/systemd").symlink_to(outside, target_is_directory=True)
    with pytest.raises(EvidenceError):
        collect_evidence(root, capability=capability)
    root2, capability2 = create_isolated_root(
        tmp_path, purpose="M122A_EVIDENCE", transaction_id="tx_evidence_2"
    )
    with pytest.raises(EvidenceError):
        collect_evidence(
            root2,
            capability=capability2,
            facts={"large": "x" * 5000},
        )
