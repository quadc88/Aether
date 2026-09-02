import pytest

from aether.deployment.manifest_schema import (
    ManifestError,
    parse_canonical_json,
    validate_revocations,
    validate_rotation_policy,
    validate_manifest,
)


def test_manifest_json_rejects_duplicate_and_noncanonical_fields():
    with pytest.raises(ManifestError):
        parse_canonical_json(b'{"a":1,"a":2}')
    with pytest.raises(ManifestError):
        parse_canonical_json(b'{"z":1,"a":2}')


def test_manifest_schema_rejects_path_escape_and_missing_lock_binding():
    manifest = {
        "manifest_version": 1,
        "release_id_format": "r1-<64 lowercase hexadecimal manifest digest>",
        "source": {"commit": "a" * 40, "tree": "b" * 40, "root_digest": "c" * 64},
        "runtime": {"python": "/usr/bin/python3.11", "python_version": "3.11", "import_root": "/opt/aether/lib"},
        "dependencies": {"closure_status": "INCOMPLETE", "artifacts": [], "direct_requirements": [], "interpreter": "cp311", "platform": "linux_x86_64", "format_version": 1, "install_policy": "offline-only; refuse installation when closure_status is INCOMPLETE", "requirements_source": "requirements.txt", "lock_digest": "d" * 64},
        "build": {"builder": "test", "reproducible": True, "unit_bundle_digest": "e" * 64, "unit_generation_id": "g-" + "f" * 64, "dependency_lock_digest": "d" * 64},
        "files": [{"path": "../escape", "sha256": "1" * 64, "size": 1, "mode": "0444", "type": "regular"}],
        "units": [{"name": name, "sha256": "2" * 64, "size": 1} for name in ("aether-oas.service", "aether-oas-runtime.socket", "aether-oas-bootstrap.socket", "aether-oas-broker.socket")],
        "schema_compatibility": {"schema_before": 1, "schema_after": 1, "mode": "UNCHANGED"},
        "policy": {"release_id": "manifest-derived", "max_retained_releases": 3},
    }
    with pytest.raises(ManifestError):
        validate_manifest(manifest)
    manifest["files"][0]["path"] = "artifact"
    del manifest["dependencies"]["lock_digest"]
    with pytest.raises(ManifestError):
        validate_manifest(manifest)


def test_rotation_and_revocation_schemas_are_closed_and_typed():
    policy = {"mode": "NORMAL", "overlap_not_before_utc": None, "overlap_expires_at_utc": None}
    assert validate_rotation_policy(policy) == policy
    assert validate_revocations(
        [{"key_id": "release-1", "revoked_at_utc": "2026-01-01T00:00:00+00:00"}],
        known_key_ids={"release-1"},
    )
    with pytest.raises(ManifestError):
        validate_rotation_policy({**policy, "unexpected": False})
    with pytest.raises(ManifestError):
        validate_revocations(
            [{"key_id": "unknown", "revoked_at_utc": "2026-01-01T00:00:00+00:00"}],
            known_key_ids={"release-1"},
        )


def test_complete_dependency_closure_cannot_be_empty():
    dependencies = {
        "closure_status": "COMPLETE", "artifacts": [], "direct_requirements": [],
        "interpreter": "cp311", "platform": "linux_x86_64", "format_version": 1,
        "install_policy": "offline-only; refuse installation when closure_status is INCOMPLETE",
        "requirements_source": "requirements.txt", "lock_digest": "a" * 64,
    }
    with pytest.raises(ManifestError):
        from aether.deployment.manifest_schema import _validate_nested_manifest
        _validate_nested_manifest({
            "source": {"commit": "a" * 40, "tree": "b" * 40, "root_digest": "c" * 64},
            "runtime": {"python": "/usr/bin/python3.11", "python_version": "3.11", "import_root": "/opt/aether/lib"},
            "dependencies": dependencies,
            "build": {"builder": "test", "reproducible": True, "unit_bundle_digest": "d" * 64, "unit_generation_id": "g-" + "e" * 64, "dependency_lock_digest": "a" * 64},
            "files": [{"path": "a", "sha256": "f" * 64, "size": 1, "mode": "0444", "type": "regular"}],
            "units": [{"name": name, "sha256": "1" * 64, "size": 1} for name in ("aether-oas.service", "aether-oas-runtime.socket", "aether-oas-bootstrap.socket", "aether-oas-broker.socket")],
            "schema_compatibility": {"schema_before": 1, "schema_after": 1, "mode": "UNCHANGED"},
            "policy": {"release_id": "manifest-derived", "max_retained_releases": 3},
        })
