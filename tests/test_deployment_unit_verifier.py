from pathlib import Path
import pytest

from aether.deployment.unit_verifier import UnitVerificationError, verify_unit_directory


def test_all_four_units_are_verified_as_one_generation():
    generation, digest = verify_unit_directory(Path(__file__).parents[1] / "deployment/systemd")
    assert generation == "g-" + digest


def test_unit_generation_rejects_tampered_bytes_and_expected_generation(tmp_path: Path):
    root = Path(__file__).parents[1] / "deployment/systemd"
    for path in root.glob("*.service"):
        (tmp_path / path.name).write_bytes(path.read_bytes() + b"\n")
    for path in root.glob("*.socket"):
        (tmp_path / path.name).write_bytes(path.read_bytes())
    with pytest.raises(UnitVerificationError):
        verify_unit_directory(tmp_path)
