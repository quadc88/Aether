"""Behavioral proof for the resumed fourth corrective M127A foundation pass."""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import threading

import pytest

from aether.deployment.host_trust_bootstrap import (
    AUTHORIZATION_DOMAIN,
    AUTHORITY_SET_FIELDS,
    GOVERNANCE_DOMAIN,
    LOCAL_CONSOLE_DOMAIN,
    OBJECT_PATHS,
    PUBLICATION_ORDER,
    STAGING_ROOT,
    STATE_DB,
    AuthoritySetVerifier,
    AuthorizationVerifier,
    GovernanceEvidenceVerifier,
    HostTrustBootstrapError,
    HostTrustBootstrapFoundation,
    HostTrustBootstrapInterrupted,
    IMAGE_BASELINE_DOMAIN,
    ImageBaselineVerifier,
    LocalConsoleEvidenceVerifier,
    TrustBootstrapState,
    TrustVerificationContext,
    VerifiedAuthorization,
    authority_key_fingerprint,
    authority_set_fingerprint,
    authorization_signing_input,
    object_set_digest,
    parse_external_record,
)
from aether.deployment.lifecycle import create_isolated_root
from aether.deployment.manifest_schema import canonical_json_bytes


PUB0 = "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"
PUB1 = "PUAXw-hDiVqStwqnTRt-vJyYLM8uxJaMwM1V8Sr0Zgw"
PUB2 = "t0A8W2NzdriyFDfrzFe68ZGKZ5xOd3A2VJYhbKRpf6E"
PUB3 = "ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ"
AUTH_KEY_FP = "f6bacf36af9ac7edd4d5b3d282686ce233e1bf034c5effcf06b7962ab287b0fb"
AUTH_SET_FP = "d0c71176f4a5e703577f40718ad79ca7ea0fa06c21b15eec65241f492a0c27e8"
BASELINE_DIGEST = "a726a64a0c3c1c34aceb3f767d2292a96c16b1f7e433049bae88442a33c32fbe"
OBJECT_DIGEST = "3cc2c330188aa205c7c7cf415236f87dfd97ec62c2281eebd37a5ec2015f80e2"
LOCAL_DIGEST = "7449ecc6cd17fe1b912c81a035f98f077c3548d03a1615a5d473a190e2864810"
GOVERNANCE_DIGEST = "20f68af26c0ec0dde3e215a7d5dba6856811c6f223334818975ca7cea58f0789"
PAYLOAD_DIGEST = "08d107e3f13a5654dcb27f3fc93c0ca27fb79184f06c1c03441fef4f7efee8c4"
BASELINE_SIG = "N1uRw_8zP-8v6H0zk2K3vkyDHRDTXExjq5SzsNQkSwUsqfUM9ILMki7R2rqRQ90251JL_BedW7bAvb5DVHRBBQ"
LOCAL_SIG = "XdAmKTL9gvhUjudrA1wsGgc4-c4SmQaupdLMookzWjCrw_KXbR1Z83LY93k4kwAyXMlCxVoLqP1bzE8LW5ddBg"
GOVERNANCE_SIG = "c53DSPXmrnGUCoEG58uV7quLz7eymg9AEYbw-hRAJVMQ-IpEtKmspELwchqcXO9Y0i1jDiBkIMZ0L5rkc2L-DQ"
AUTHORIZATION_SIG = "0LcQrrSSzrfCTVjLsjFO8y_1CQnZTgCq0lm_u5aBYfWBcnlqGw75oTofwI6dx_FKZjxBTN7vawH9bWFbTSRvBA"


def _b64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "===")


def _raw(value: dict[str, object]) -> bytes:
    return canonical_json_bytes(value)


def _ephemeral_key(tmp_path: Path, name: str) -> tuple[Path, Path, bytes]:
    """Create one disposable Ed25519 key and return only its public bytes."""

    private = tmp_path / f"{name}.pem"
    public = tmp_path / f"{name}.der"
    subprocess.run(
        ["/usr/bin/openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(
        ["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-outform", "DER", "-out", str(public)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    der = public.read_bytes()
    prefix = bytes.fromhex("302a300506032b6570032100")
    assert der.startswith(prefix) and len(der) == len(prefix) + 32
    return private, public, der[len(prefix):]


def _sign_ephemeral(tmp_path: Path, private: Path, message: bytes, name: str) -> str:
    source = tmp_path / f"{name}.message"
    signature = tmp_path / f"{name}.signature"
    try:
        source.write_bytes(message)
        subprocess.run(
            ["/usr/bin/openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private), "-in", str(source), "-out", str(signature)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return base64.urlsafe_b64encode(signature.read_bytes()).decode().rstrip("=")
    finally:
        source.unlink(missing_ok=True)
        signature.unlink(missing_ok=True)


def _signed_valid_fixture_bundle(tmp_path: Path, specifications: list[dict[str, object]]) -> dict[str, object]:
    """Build valid competing records, then destroy every disposable private key."""

    private_paths: list[Path] = []
    public_paths: list[Path] = []
    try:
        image_private, image_public_path, image_public = _ephemeral_key(tmp_path, "m127a-image")
        authority_private, authority_public_path, authority_public = _ephemeral_key(tmp_path, "m127a-authority")
        local_private, local_public_path, local_public = _ephemeral_key(tmp_path, "m127a-local")
        governance_private, governance_public_path, governance_public = _ephemeral_key(tmp_path, "m127a-governance")
        private_paths.extend((image_private, authority_private, local_private, governance_private))
        public_paths.extend((image_public_path, authority_public_path, local_public_path, governance_public_path))

        authority_record = {
            "authority_id": "ephemeral-host-authority",
            "authority_role": "HOST_TRUST_BOOTSTRAP_AUTHORITY",
            "algorithm": "Ed25519",
            "public_key_base64url": base64.urlsafe_b64encode(authority_public).decode().rstrip("="),
            "key_fingerprint_sha256": "",
            "authority_generation": 1,
            "valid_from_utc": "2026-01-01T00:00:00+00:00",
            "valid_until_utc": "2027-01-01T00:00:00+00:00",
            "revoked_at_utc": None,
        }
        authority_record["key_fingerprint_sha256"] = authority_key_fingerprint(authority_record)
        authority_set = {
            "authority_set_version": 1,
            "baseline_id": "ephemeral-image-baseline",
            "authority_records": [authority_record],
            "minimum_accepted_authority_generation": 1,
            "set_fingerprint_sha256": "",
            "image_baseline_manifest_digest": "1" * 64,
        }
        authority_set["set_fingerprint_sha256"] = authority_set_fingerprint(authority_set)
        authority_raw = _raw(authority_set)
        baseline_digest = hashlib.sha256(authority_raw).hexdigest()
        baseline_signature = _sign_ephemeral(
            tmp_path,
            image_private,
            IMAGE_BASELINE_DOMAIN.encode("ascii") + b"\0" + authority_raw,
            "m127a-image-baseline",
        )
        image_private.unlink(missing_ok=True)
        assert not image_private.exists()
        authority_root = authority_set["set_fingerprint_sha256"]

        cases: dict[str, object] = {}
        for index, specification in enumerate(specifications):
            generation = specification["trust_generation"]
            objects = {
                OBJECT_PATHS[0]: _raw({"anchor_version": 1, "anchor_id": f"ephemeral-anchor-{generation}", "keys": []}),
                OBJECT_PATHS[1]: (f"{authority_root}\n").encode("ascii"),
                OBJECT_PATHS[2]: ("2" * 64 + "\n").encode("ascii"),
                OBJECT_PATHS[4]: f"fixed-verifier-ephemeral-generation-{generation}\n".encode("ascii"),
            }
            objects[OBJECT_PATHS[3]] = (hashlib.sha256(objects[OBJECT_PATHS[4]]).hexdigest() + "\n").encode("ascii")
            objects_digest = object_set_digest(objects)
            issued = "2026-09-03T11:00:00+00:00"
            expires = "2026-09-03T13:00:00+00:00"
            local = {
                "evidence_version": 1,
                "attestation_id": f"ephemeral-attestation-{index}",
                "target_host_identity_digest": "2" * 64,
                "target_boot_digest": "3" * 64,
                "bootstrap_authority_root_fingerprint": authority_root,
                "bootstrap_authority_generation": 1,
                "authority_set_record_digest": baseline_digest,
                "local_console_authority_id": "ephemeral-local-console",
                "session_class": "LOCAL_CONSOLE",
                "remote": False,
                "fresh_authentication": True,
                "human_confirmation_digest": f"{index + 4:x}" * 64,
                "issued_at_utc": issued,
                "expires_at_utc": expires,
                "nonce": specification["nonce"],
                "evidence_algorithm": "ED25519_DETACHED_SIGNATURE_V1",
                "authenticated_evidence": "LOCAL_CONSOLE_VERIFIER_V1",
            }
            local_raw = _raw(local)
            local_signature = _sign_ephemeral(
                tmp_path,
                local_private,
                LOCAL_CONSOLE_DOMAIN.encode("ascii") + b"\0" + local_raw,
                f"m127a-local-{index}",
            )
            governance = {
                "evidence_version": 1,
                "governance_evidence_id": f"ephemeral-governance-{index}",
                "milestone": "M127A",
                "approved_scope_digest": "5" * 64,
                "approved_policy_digest": "6" * 64,
                "approved_object_set_digest": objects_digest,
                "approved_generation_policy_digest": "7" * 64,
                "issuer_role": "PM_GOVERNANCE",
                "issuer_authority_id": "ephemeral-pm-authority",
                "issued_at_utc": issued,
                "expires_at_utc": expires,
                "authenticated_evidence_algorithm": "ED25519_DETACHED_SIGNATURE_V1",
                "authenticated_evidence": "GOVERNANCE_VERIFIER_V1",
            }
            governance_raw = _raw(governance)
            governance_signature = _sign_ephemeral(
                tmp_path,
                governance_private,
                GOVERNANCE_DOMAIN.encode("ascii") + b"\0" + governance_raw,
                f"m127a-governance-{index}",
            )
            payload = {
                "payload_version": 1,
                "authorization_id": specification["authorization_id"],
                "transaction_id": specification["transaction_id"],
                "target_host_identity_digest": "2" * 64,
                "target_boot_digest": "3" * 64,
                "trust_generation": generation,
                "minimum_accepted_generation": specification["minimum_accepted_generation"],
                "object_set_digest": objects_digest,
                "requested_objects": list(OBJECT_PATHS),
                "mutation_scope": "PUBLISH_EXACT_FIVE_HOST_TRUST_OBJECTS_FOR_TARGET_HOST_AND_GENERATION",
                "local_console_attestation_digest": hashlib.sha256(local_raw).hexdigest(),
                "governance_scope_digest": hashlib.sha256(governance_raw).hexdigest(),
                "bootstrap_authority_root_fingerprint": authority_root,
                "bootstrap_authority_generation": 1,
                "authority_set_record_digest": baseline_digest,
                "issued_at_utc": issued,
                "expires_at_utc": expires,
                "nonce": specification["nonce"],
            }
            payload_raw = _raw(payload)
            envelope = {
                "envelope_version": 1,
                "payload_sha256": hashlib.sha256(payload_raw).hexdigest(),
                "authorizing_role": "HOST_TRUST_BOOTSTRAP_AUTHORITY",
                "authorizing_authority_id": authority_record["authority_id"],
                "authenticated_evidence_algorithm": "ED25519_DETACHED_SIGNATURE_V1",
                "detached_signature": "A" * 86,
                "verification_key_or_trust_source": {
                    "source_kind": "PREEXISTING_OS_IMAGE_AUTHORITY_SET",
                    "authority_set_path": "/usr/lib/aether/host-bootstrap/authority-set.json",
                    "authority_set_record_digest": baseline_digest,
                    "authority_id": authority_record["authority_id"],
                    "key_fingerprint_sha256": authority_record["key_fingerprint_sha256"],
                    "authority_generation": 1,
                    "image_baseline_manifest_digest": "1" * 64,
                },
                "issued_at_utc": issued,
                "expires_at_utc": expires,
                "target_host_identity_digest": "2" * 64,
                "target_boot_digest": "3" * 64,
                "bootstrap_authority_root_fingerprint": authority_root,
                "bootstrap_authority_generation": 1,
                "authority_set_record_digest": baseline_digest,
                "trust_generation": generation,
                "object_set_digest": objects_digest,
                "nonce": specification["nonce"],
                "transaction_id": specification["transaction_id"],
                "domain_separator": AUTHORIZATION_DOMAIN,
            }
            authorization_signature = _sign_ephemeral(
                tmp_path,
                authority_private,
                AUTHORIZATION_DOMAIN.encode("ascii") + b"\0" + payload_raw + b"\0" + _raw({key: value for key, value in envelope.items() if key != "detached_signature"}),
                f"m127a-authorization-{index}",
            )
            envelope["detached_signature"] = authorization_signature
            cases[specification["name"]] = {
                "local_raw": local_raw,
                "local_signature": local_signature,
                "governance_raw": governance_raw,
                "governance_signature": governance_signature,
                "payload_raw": payload_raw,
                "envelope_raw": _raw(envelope),
                "objects": objects,
                "transaction_id": specification["transaction_id"],
                "nonce": specification["nonce"],
                "trust_generation": generation,
            }
        for path in (authority_private, local_private, governance_private):
            path.unlink(missing_ok=True)
        assert all(not path.exists() for path in (authority_private, local_private, governance_private))
        return {
            "context": TrustVerificationContext.create(
                image_baseline_public_key=image_public,
                expected_baseline_digest=baseline_digest,
                local_console_public_key=local_public,
                governance_public_key=governance_public,
            ),
            "authority_raw": authority_raw,
            "authority_signature": baseline_signature,
            "cases": cases,
        }
    finally:
        for path in private_paths + public_paths:
            path.unlink(missing_ok=True)
        assert all(not path.exists() for path in private_paths)


def _context(*, image_key: str = PUB1, baseline_digest: str = BASELINE_DIGEST) -> TrustVerificationContext:
    return TrustVerificationContext.create(
        image_baseline_public_key=_b64(image_key), expected_baseline_digest=baseline_digest,
        local_console_public_key=_b64(PUB2), governance_public_key=_b64(PUB3),
    )


def _fixtures() -> dict[str, object]:
    authority_record = {
        "authority_id": "host-authority-1", "authority_role": "HOST_TRUST_BOOTSTRAP_AUTHORITY",
        "algorithm": "Ed25519", "public_key_base64url": PUB0, "key_fingerprint_sha256": AUTH_KEY_FP,
        "authority_generation": 1, "valid_from_utc": "2026-01-01T00:00:00+00:00",
        "valid_until_utc": "2027-01-01T00:00:00+00:00", "revoked_at_utc": None,
    }
    authority_set = {
        "authority_set_version": 1, "baseline_id": "image-baseline-1", "authority_records": [authority_record],
        "minimum_accepted_authority_generation": 1, "set_fingerprint_sha256": AUTH_SET_FP,
        "image_baseline_manifest_digest": "1" * 64,
    }
    authority_raw = _raw(authority_set)
    objects: dict[str, bytes] = {
        OBJECT_PATHS[0]: _raw({"anchor_version": 1, "anchor_id": "fixture-anchor", "keys": []}),
        OBJECT_PATHS[1]: (AUTH_SET_FP + "\n").encode("ascii"),
        OBJECT_PATHS[2]: ("2" * 64 + "\n").encode("ascii"),
        OBJECT_PATHS[4]: b"fixed-verifier-fixture-v1\n",
    }
    objects[OBJECT_PATHS[3]] = (hashlib.sha256(objects[OBJECT_PATHS[4]]).hexdigest() + "\n").encode("ascii")
    local = {
        "evidence_version": 1, "attestation_id": "attestation-1", "target_host_identity_digest": "2" * 64,
        "target_boot_digest": "3" * 64, "bootstrap_authority_root_fingerprint": AUTH_SET_FP,
        "bootstrap_authority_generation": 1, "authority_set_record_digest": BASELINE_DIGEST,
        "local_console_authority_id": "local-console-authority-1", "session_class": "LOCAL_CONSOLE",
        "remote": False, "fresh_authentication": True, "human_confirmation_digest": "4" * 64,
        "issued_at_utc": "2026-09-03T11:00:00+00:00", "expires_at_utc": "2026-09-03T13:00:00+00:00",
        "nonce": "nonce-127a-1", "evidence_algorithm": "ED25519_DETACHED_SIGNATURE_V1",
        "authenticated_evidence": "LOCAL_CONSOLE_VERIFIER_V1",
    }
    governance = {
        "evidence_version": 1, "governance_evidence_id": "governance-1", "milestone": "M127A",
        "approved_scope_digest": "5" * 64, "approved_policy_digest": "6" * 64,
        "approved_object_set_digest": OBJECT_DIGEST, "approved_generation_policy_digest": "7" * 64,
        "issuer_role": "PM_GOVERNANCE", "issuer_authority_id": "pm-authority-1",
        "issued_at_utc": "2026-09-03T11:00:00+00:00", "expires_at_utc": "2026-09-03T13:00:00+00:00",
        "authenticated_evidence_algorithm": "ED25519_DETACHED_SIGNATURE_V1", "authenticated_evidence": "GOVERNANCE_VERIFIER_V1",
    }
    payload = {
        "payload_version": 1, "authorization_id": "authorization-1", "transaction_id": "tx-m127a",
        "target_host_identity_digest": "2" * 64, "target_boot_digest": "3" * 64, "trust_generation": 2,
        "minimum_accepted_generation": 1, "object_set_digest": OBJECT_DIGEST, "requested_objects": list(OBJECT_PATHS),
        "mutation_scope": "PUBLISH_EXACT_FIVE_HOST_TRUST_OBJECTS_FOR_TARGET_HOST_AND_GENERATION",
        "local_console_attestation_digest": LOCAL_DIGEST, "governance_scope_digest": GOVERNANCE_DIGEST,
        "bootstrap_authority_root_fingerprint": AUTH_SET_FP, "bootstrap_authority_generation": 1,
        "authority_set_record_digest": BASELINE_DIGEST, "issued_at_utc": "2026-09-03T11:00:00+00:00",
        "expires_at_utc": "2026-09-03T13:00:00+00:00", "nonce": "nonce-127a-1",
    }
    envelope = {
        "envelope_version": 1, "payload_sha256": PAYLOAD_DIGEST, "authorizing_role": "HOST_TRUST_BOOTSTRAP_AUTHORITY",
        "authorizing_authority_id": "host-authority-1", "authenticated_evidence_algorithm": "ED25519_DETACHED_SIGNATURE_V1",
        "detached_signature": AUTHORIZATION_SIG,
        "verification_key_or_trust_source": {"source_kind": "PREEXISTING_OS_IMAGE_AUTHORITY_SET", "authority_set_path": "/usr/lib/aether/host-bootstrap/authority-set.json", "authority_set_record_digest": BASELINE_DIGEST, "authority_id": "host-authority-1", "key_fingerprint_sha256": AUTH_KEY_FP, "authority_generation": 1, "image_baseline_manifest_digest": "1" * 64},
        "issued_at_utc": payload["issued_at_utc"], "expires_at_utc": payload["expires_at_utc"],
        "target_host_identity_digest": payload["target_host_identity_digest"], "target_boot_digest": payload["target_boot_digest"],
        "bootstrap_authority_root_fingerprint": AUTH_SET_FP, "bootstrap_authority_generation": 1,
        "authority_set_record_digest": BASELINE_DIGEST, "trust_generation": 2, "object_set_digest": OBJECT_DIGEST,
        "nonce": "nonce-127a-1", "transaction_id": "tx-m127a", "domain_separator": AUTHORIZATION_DOMAIN,
    }
    return {"authority_raw": authority_raw, "objects": objects, "local_raw": _raw(local), "governance_raw": _raw(governance), "payload_raw": _raw(payload), "envelope_raw": _raw(envelope)}


def _verified_parts(context: TrustVerificationContext) -> tuple[object, object, object]:
    f = _fixtures()
    baseline = ImageBaselineVerifier(context).verify(f["authority_raw"], BASELINE_SIG)
    authority = AuthoritySetVerifier().verify(baseline)
    local = LocalConsoleEvidenceVerifier(context).verify(f["local_raw"], LOCAL_SIG)
    governance = GovernanceEvidenceVerifier(context).verify(f["governance_raw"], GOVERNANCE_SIG)
    return authority, local, governance


def _authorization(context: TrustVerificationContext | None = None, *, now: str = "2026-09-03T12:00:00+00:00") -> VerifiedAuthorization:
    context = context or _context()
    f = _fixtures()
    authority, local, governance = _verified_parts(context)
    return AuthorizationVerifier(context).verify(f["payload_raw"], f["envelope_raw"], authority=authority, local_console=local, governance=governance, target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=now)


def _dynamic_authorization(bundle: dict[str, object], name: str, *, now: str = "2026-09-03T12:00:00+00:00") -> VerifiedAuthorization:
    context = bundle["context"]
    fixture = bundle["cases"][name]
    baseline = ImageBaselineVerifier(context).verify(bundle["authority_raw"], bundle["authority_signature"])
    authority = AuthoritySetVerifier().verify(baseline)
    local = LocalConsoleEvidenceVerifier(context).verify(fixture["local_raw"], fixture["local_signature"])
    governance = GovernanceEvidenceVerifier(context).verify(fixture["governance_raw"], fixture["governance_signature"])
    return AuthorizationVerifier(context).verify(
        fixture["payload_raw"],
        fixture["envelope_raw"],
        authority=authority,
        local_console=local,
        governance=governance,
        target_host_identity_digest="2" * 64,
        target_boot_digest="3" * 64,
        now_utc=now,
    )


def _foundation(parent: Path, context: TrustVerificationContext, *, fault=None, now: str = "2026-09-03T12:00:00+00:00", timeout: float = 0.25) -> tuple[Path, HostTrustBootstrapFoundation]:
    root, capability = create_isolated_root(parent, purpose="M127A_BOOTSTRAP", transaction_id="tx-m127a")
    foundation = HostTrustBootstrapFoundation(root, capability=capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, fault_injector=fault, now_utc=lambda: now, lock_timeout_seconds=timeout)
    return root, foundation


def _assert_rejected(context: TrustVerificationContext, envelope: dict[str, object]) -> None:
    f = _fixtures()
    authority, local, governance = _verified_parts(context)
    with pytest.raises(HostTrustBootstrapError):
        AuthorizationVerifier(context).verify(f["payload_raw"], _raw(envelope), authority=authority, local_console=local, governance=governance, target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc="2026-09-03T12:00:00+00:00")


def test_context_bound_precomputed_signature_and_m126a_fingerprints():
    f = _fixtures()
    context = _context()
    authority_set, raw = parse_external_record(f["authority_raw"], AUTHORITY_SET_FIELDS, "authority set")
    assert authority_key_fingerprint(authority_set["authority_records"][0]) == AUTH_KEY_FP
    assert authority_set_fingerprint(authority_set) == AUTH_SET_FP
    assert hashlib.sha256(raw).hexdigest() == BASELINE_DIGEST
    assert object_set_digest(f["objects"]) == OBJECT_DIGEST
    authorization = _authorization(context)
    assert authorization.context is context
    assert authorization_signing_input(f["payload_raw"], f["envelope_raw"]).startswith(AUTHORIZATION_DOMAIN.encode() + b"\0")


def test_context_has_distinct_process_identity_and_restart_stable_durable_fingerprint():
    first = _context()
    second = _context()
    changed_key = _context(image_key=PUB0)
    changed_digest = _context(baseline_digest="f" * 64)
    assert first.process_identity is not second.process_identity
    assert first.durable_fingerprint == second.durable_fingerprint == first.binding_digest
    assert changed_key.durable_fingerprint != first.durable_fingerprint
    assert changed_digest.durable_fingerprint != first.durable_fingerprint

    code = """
from aether.deployment.host_trust_bootstrap import TrustVerificationContext
import base64
def b(value): return base64.urlsafe_b64decode(value + '===')
context = TrustVerificationContext.create(image_baseline_public_key=b('PUAXw-hDiVqStwqnTRt-vJyYLM8uxJaMwM1V8Sr0Zgw'), expected_baseline_digest='a726a64a0c3c1c34aceb3f767d2292a96c16b1f7e433049bae88442a33c32fbe', local_console_public_key=b('t0A8W2NzdriyFDfrzFe68ZGKZ5xOd3A2VJYhbKRpf6E'), governance_public_key=b('ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ'))
print(context.durable_fingerprint)
"""
    child = subprocess.run([sys.executable, "-c", code], cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True)
    assert child.stdout.strip() == first.durable_fingerprint


def test_arbitrary_verifier_and_public_key_substitution_cannot_cross_context(tmp_path):
    f = _fixtures()
    context = _context()
    wrong_context = _context(image_key=PUB0)
    with pytest.raises(HostTrustBootstrapError):
        ImageBaselineVerifier(wrong_context).verify(f["authority_raw"], BASELINE_SIG)
    with pytest.raises(HostTrustBootstrapError):
        ImageBaselineVerifier(_context(baseline_digest="f" * 64)).verify(f["authority_raw"], BASELINE_SIG)
    verifier = ImageBaselineVerifier(context)
    with pytest.raises(AttributeError):
        verifier.context = wrong_context
    copied = _authorization(_context())
    _, foundation = _foundation(tmp_path, context)
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(copied, f["objects"])
    with pytest.raises(HostTrustBootstrapError):
        AuthorizationVerifier(context).verify(f["payload_raw"], f["envelope_raw"], authority=_verified_parts(context)[0], local_console=_verified_parts(wrong_context)[1], governance=_verified_parts(context)[2], target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc="2026-09-03T12:00:00+00:00")


def test_wrong_typed_domain_result_is_insufficient():
    context = _context()
    authority, local, governance = _verified_parts(context)
    with pytest.raises(HostTrustBootstrapError):
        AuthorizationVerifier(context).verify(_fixtures()["payload_raw"], _fixtures()["envelope_raw"], authority=authority, local_console=governance, governance=local, target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc="2026-09-03T12:00:00+00:00")


@pytest.mark.parametrize("field", [
    "envelope_version", "payload_sha256", "authorizing_role", "authorizing_authority_id",
    "authenticated_evidence_algorithm", "verification_key_or_trust_source.source_kind",
    "verification_key_or_trust_source.authority_set_path", "verification_key_or_trust_source.authority_set_record_digest",
    "verification_key_or_trust_source.authority_id", "verification_key_or_trust_source.key_fingerprint_sha256",
    "verification_key_or_trust_source.authority_generation", "verification_key_or_trust_source.image_baseline_manifest_digest",
    "issued_at_utc", "expires_at_utc", "target_host_identity_digest", "target_boot_digest",
    "bootstrap_authority_root_fingerprint", "bootstrap_authority_generation", "trust_generation",
    "object_set_digest", "nonce", "transaction_id", "domain_separator", "detached_signature",
])
def test_every_signed_envelope_field_rejects_independent_tampering(field):
    envelope = json.loads(_fixtures()["envelope_raw"])
    if "." in field:
        parent, child = field.split(".")
        envelope[parent][child] = 2 if child.endswith("generation") or child == "authority_generation" else "changed"
    elif field in {"envelope_version", "bootstrap_authority_generation"}:
        envelope[field] = 2
    elif field == "trust_generation":
        envelope[field] = 3
    elif field == "detached_signature":
        envelope[field] = "A" + envelope[field][1:]
    else:
        envelope[field] = "f" * 64 if "digest" in field or field == "payload_sha256" else "changed"
    _assert_rejected(_context(), envelope)


@pytest.mark.parametrize("field", [
    "target_host_identity_digest", "target_boot_digest", "bootstrap_authority_root_fingerprint",
    "bootstrap_authority_generation", "authority_set_record_digest", "local_console_authority_id",
    "session_class", "remote", "fresh_authentication", "human_confirmation_digest", "issued_at_utc",
    "expires_at_utc", "nonce", "evidence_algorithm", "authenticated_evidence",
])
def test_every_local_console_field_and_signature_rejects_tampering(field):
    context = _context()
    local = json.loads(_fixtures()["local_raw"])
    local[field] = 2 if field == "bootstrap_authority_generation" else (False if field == "fresh_authentication" else (True if field == "remote" else "changed"))
    with pytest.raises(HostTrustBootstrapError):
        LocalConsoleEvidenceVerifier(context).verify(_raw(local), LOCAL_SIG)


@pytest.mark.parametrize("field", [
    "milestone", "approved_scope_digest", "approved_policy_digest", "approved_object_set_digest",
    "approved_generation_policy_digest", "issuer_role", "issuer_authority_id", "issued_at_utc", "expires_at_utc",
    "authenticated_evidence_algorithm", "authenticated_evidence",
])
def test_every_governance_field_and_signature_rejects_tampering(field):
    context = _context()
    governance = json.loads(_fixtures()["governance_raw"])
    governance[field] = "changed"
    with pytest.raises(HostTrustBootstrapError):
        GovernanceEvidenceVerifier(context).verify(_raw(governance), GOVERNANCE_SIG)


def test_raw_record_substitution_duplicate_noncanonical_and_result_mutation_fail():
    f = _fixtures()
    with pytest.raises(HostTrustBootstrapError):
        parse_external_record(b" " + f["payload_raw"], tuple(json.loads(f["payload_raw"])), "payload")
    with pytest.raises(HostTrustBootstrapError):
        parse_external_record(f["payload_raw"].replace(b'"nonce":"nonce-127a-1"', b'"nonce":"nonce-127a-1","nonce":"nonce-127a-1"', 1), tuple(json.loads(f["payload_raw"])), "payload")
    authorization = _authorization()
    with pytest.raises(TypeError):
        authorization.payload["nonce"] = "changed"
    with pytest.raises(AttributeError):
        authorization.context = _context()
    with pytest.raises(TypeError):
        VerifiedAuthorization(object(), b"", {}, b"", {}, authorization.authority, authorization.local_console, authorization.governance, authorization.context)


def test_successful_bootstrap_commits_terminal_observation_and_verification(tmp_path):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    result = foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    assert result.state == TrustBootstrapState.ACTIVE.value
    for path, data in _fixtures()["objects"].items():
        target = root / path.lstrip("/")
        assert target.read_bytes() == data
        assert (target.stat().st_mode & 0o777) == (0o555 if path.endswith("aether-release-verify") else 0o444)
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1


def test_expiry_before_intent_and_immediately_before_intent_leave_no_transaction(tmp_path):
    context = _context()
    root, foundation = _foundation(tmp_path, context, now="2026-09-03T14:00:00+00:00")
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    assert not (root / STATE_DB).exists()

    calls = {"count": 0}
    root2, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="tx-m127a")
    def clock():
        calls["count"] += 1
        return "2026-09-03T12:59:00+00:00" if calls["count"] == 1 else "2026-09-03T13:00:00+00:00"
    foundation2 = HostTrustBootstrapFoundation(root2, capability=capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=clock)
    with pytest.raises(HostTrustBootstrapError):
        foundation2.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root2 / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 0


def test_expiry_after_requested_allows_only_frozen_recovery_and_changed_retry_fails(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_TRUST_BOOTSTRAP_REQUESTED" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault, now="2026-09-03T12:00:00+00:00")
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    expired = HostTrustBootstrapFoundation(root, capability=foundation.capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=lambda: "2026-09-03T14:00:00+00:00")
    result = expired.bootstrap(_authorization(context), _fixtures()["objects"])
    assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
    changed = dict(_fixtures()["objects"])
    changed[OBJECT_PATHS[4]] = b"changed\n"
    with pytest.raises(HostTrustBootstrapError):
        expired.bootstrap(_authorization(context), changed)


def test_failed_generation_is_burned_and_never_becomes_active_or_reusable(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_TRUST_BOOTSTRAP_REQUESTED" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    result = foundation.recover("tx-m127a")
    assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT reservation_state FROM generation_reservations WHERE trust_generation=2").fetchone()[0] == "BURNED"
        assert db.execute("SELECT active_generation, highest_seen_or_reserved_generation, minimum_accepted_generation FROM schema_metadata").fetchone() == (0, 2, 1)
    retry = foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    assert retry == result


def test_fresh_context_raw_evidence_reconstruction_allows_only_identical_expired_intent(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_TRUST_BOOTSTRAP_REQUESTED" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    fixture = _fixtures()
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap_from_raw(
            authority_raw=fixture["authority_raw"], authority_signature=BASELINE_SIG,
            local_console_raw=fixture["local_raw"], local_console_signature=LOCAL_SIG,
            governance_raw=fixture["governance_raw"], governance_signature=GOVERNANCE_SIG,
            payload_raw=fixture["payload_raw"], envelope_raw=fixture["envelope_raw"], objects=fixture["objects"],
        )
    reconstructed = TrustVerificationContext.create(
        image_baseline_public_key=_b64(PUB1), expected_baseline_digest=BASELINE_DIGEST,
        local_console_public_key=_b64(PUB2), governance_public_key=_b64(PUB3),
    )
    restarted = HostTrustBootstrapFoundation(root, capability=foundation.capability, context=reconstructed, authorization_verifier=AuthorizationVerifier(reconstructed), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=lambda: "2026-09-03T14:00:00+00:00")
    result = restarted.bootstrap_from_raw(
        authority_raw=fixture["authority_raw"], authority_signature=BASELINE_SIG,
        local_console_raw=fixture["local_raw"], local_console_signature=LOCAL_SIG,
        governance_raw=fixture["governance_raw"], governance_signature=GOVERNANCE_SIG,
        payload_raw=fixture["payload_raw"], envelope_raw=fixture["envelope_raw"], objects=fixture["objects"],
        allow_expired_existing=True, verification_time_utc="2026-09-03T12:00:00+00:00",
    )
    assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
    changed_local = json.loads(fixture["local_raw"])
    changed_local["nonce"] = "changed-nonce"
    with pytest.raises(HostTrustBootstrapError):
        restarted.bootstrap_from_raw(
            authority_raw=fixture["authority_raw"], authority_signature=BASELINE_SIG,
            local_console_raw=_raw(changed_local), local_console_signature=LOCAL_SIG,
            governance_raw=fixture["governance_raw"], governance_signature=GOVERNANCE_SIG,
            payload_raw=fixture["payload_raw"], envelope_raw=fixture["envelope_raw"], objects=fixture["objects"],
            allow_expired_existing=True, verification_time_utc="2026-09-03T12:00:00+00:00",
        )


def test_delayed_terminal_retry_and_nonce_generation_constraints(tmp_path):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    first = foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    delayed = HostTrustBootstrapFoundation(root, capability=foundation.capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=lambda: "2027-01-01T00:00:00+00:00")
    assert delayed.bootstrap(_authorization(context), _fixtures()["objects"]) == first
    with sqlite3.connect(root / STATE_DB) as db:
        row = db.execute("SELECT * FROM transactions").fetchone()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO transactions VALUES(?,?,?,?,?)", ("different", row[1], 3, row[3], row[4]))
    assert root.exists()


def test_complete_prior_generation_is_restored_and_verified(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_ALL_WRITES" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    prior = {path: (f"prior-{index}\n").encode("ascii") for index, path in enumerate(OBJECT_PATHS)}
    for path, data in prior.items():
        target = root / path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        os.chmod(target, 0o555 if path.endswith("aether-release-verify") else 0o444)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    result = foundation.recover("tx-m127a")
    assert result.result == "PRIOR_GENERATION_RESTORED_REVIEW_REQUIRED"
    for path, data in prior.items():
        assert (root / path.lstrip("/")).read_bytes() == data


def test_tampered_retained_prior_evidence_enters_review_with_failure_class(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_ALL_WRITES" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        db.execute("UPDATE prior_objects SET content_digest=? WHERE path=?", ("0" * 64, OBJECT_PATHS[0]))
        db.commit()
    result = foundation.recover("tx-m127a")
    assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT record_json FROM transactions").fetchone()[0]


def test_recovery_evidence_corruption_fails_closed(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_ALL_WRITES" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    foundation.recover("tx-m127a")
    with sqlite3.connect(root / STATE_DB) as db:
        db.execute("UPDATE recovery_verifications SET record_digest=?", ("0" * 64,))
        db.commit()
    with pytest.raises(HostTrustBootstrapError):
        foundation.recover("tx-m127a")


FAILPOINTS = [
    "BEFORE_INTENT", "DURING_STATE_UPDATE", "BETWEEN_STATE_AND_AUDIT", "AFTER_AUDIT_BEFORE_METADATA", "AFTER_METADATA_BEFORE_COMMIT",
    "AFTER_TRUST_BOOTSTRAP_REQUESTED", "AFTER_TRUST_BOOTSTRAP_VALIDATED", "DURING_PRIOR_CAPTURE_0", "DURING_PRIOR_CAPTURE_1",
    "DURING_PRIOR_CAPTURE_2", "DURING_PRIOR_CAPTURE_3", "DURING_PRIOR_CAPTURE_4", "AFTER_PRIOR_GENERATION_RETAINED",
    "DURING_STAGE_0", "DURING_STAGE_1", "DURING_STAGE_2", "DURING_STAGE_3", "DURING_STAGE_4",
    "AFTER_STAGED_FILE_FSYNC_0", "AFTER_STAGED_FILE_FSYNC_1", "AFTER_STAGED_FILE_FSYNC_2", "AFTER_STAGED_FILE_FSYNC_3", "AFTER_STAGED_FILE_FSYNC_4",
    "AFTER_STAGING_DIRECTORY_FSYNC", "AFTER_NEXT_GENERATION_STAGED", "BEFORE_PUBLISHING", "BEFORE_PUBLISH_0", "BEFORE_PUBLISH_1", "BEFORE_PUBLISH_2", "BEFORE_PUBLISH_3", "BEFORE_PUBLISH_4",
    "AFTER_PUBLISH_0", "AFTER_PUBLISH_1", "AFTER_PUBLISH_2", "AFTER_PUBLISH_3", "AFTER_PUBLISH_4", "BETWEEN_USR_LIBEXEC_AND_ETC_PUBLICATION", "AFTER_ALL_WRITES", "BEFORE_VERIFYING", "DURING_OBSERVATION", "DURING_VERIFICATION", "AFTER_SUCCESSFUL_VERIFICATION_BEFORE_TERMINAL_COMMIT", "DURING_TERMINAL_STATE_UPDATE", "BETWEEN_TERMINAL_STATE_AND_AUDIT", "AFTER_TERMINAL_AUDIT_BEFORE_COMMIT", "AFTER_TERMINAL_METADATA_BEFORE_COMMIT", "AFTER_TERMINAL_COMMIT",
    "DURING_RESTORE_0", "DURING_RESTORE_1", "DURING_RESTORE_2", "DURING_RESTORE_3", "DURING_RESTORE_4", "DURING_RECOVERY_OBSERVATION", "DURING_RECOVERY_VERIFICATION",
]


def _expected_committed_prefix(point: str) -> int:
    if point in {"DURING_STATE_UPDATE", "BETWEEN_STATE_AND_AUDIT", "AFTER_AUDIT_BEFORE_METADATA", "AFTER_METADATA_BEFORE_COMMIT"}:
        return 0
    if point == "AFTER_TRUST_BOOTSTRAP_REQUESTED":
        return 1
    if point == "AFTER_TRUST_BOOTSTRAP_VALIDATED" or point.startswith("DURING_PRIOR_CAPTURE_"):
        return 2
    if point == "AFTER_PRIOR_GENERATION_RETAINED" or point.startswith("DURING_STAGE_") or point.startswith("AFTER_STAGED_FILE_FSYNC_") or point in {"AFTER_STAGING_DIRECTORY_FSYNC", "AFTER_NEXT_GENERATION_STAGED", "BEFORE_PUBLISHING"}:
        return 3 if point == "AFTER_PRIOR_GENERATION_RETAINED" or point.startswith("DURING_STAGE_") or point.startswith("AFTER_STAGED_FILE_FSYNC_") or point == "AFTER_STAGING_DIRECTORY_FSYNC" else 4
    if point.startswith("BEFORE_PUBLISH_") or point.startswith("AFTER_PUBLISH_") or point == "BETWEEN_USR_LIBEXEC_AND_ETC_PUBLICATION" or point == "AFTER_ALL_WRITES":
        return 5
    if point in {"BEFORE_VERIFYING", "DURING_OBSERVATION", "DURING_VERIFICATION", "AFTER_SUCCESSFUL_VERIFICATION_BEFORE_TERMINAL_COMMIT"}:
        return 6
    if point in {"DURING_TERMINAL_STATE_UPDATE", "BETWEEN_TERMINAL_STATE_AND_AUDIT", "AFTER_TERMINAL_AUDIT_BEFORE_COMMIT", "AFTER_TERMINAL_METADATA_BEFORE_COMMIT"}:
        return 6
    if point == "AFTER_TERMINAL_COMMIT":
        return 7
    return 5


@pytest.mark.parametrize("point", FAILPOINTS)
def test_complete_failpoint_matrix_has_exact_restart_outcome(tmp_path, point):
    fired = {"value": False}
    def fault(name):
        if name == point and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    context = _context()
    if point.startswith("DURING_RESTORE") or point.startswith("DURING_RECOVERY"):
        def recovery_fault(name):
            if name == "AFTER_ALL_WRITES" and not fired["value"]:
                fired["value"] = True
                raise HostTrustBootstrapInterrupted(name)
            if name == point:
                raise HostTrustBootstrapInterrupted(point)
        root, foundation = _foundation(tmp_path, context, fault=recovery_fault)
        with pytest.raises(HostTrustBootstrapInterrupted):
            foundation.bootstrap(_authorization(context), _fixtures()["objects"])
        restarted = HostTrustBootstrapFoundation(root, capability=foundation.capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, fault_injector=recovery_fault, now_utc=lambda: "2026-09-03T12:00:00+00:00")
        result = restarted.recover("tx-m127a")
        assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
        with sqlite3.connect(root / STATE_DB) as db:
            assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
            assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
            assert db.execute("SELECT reservation_state FROM generation_reservations").fetchone()[0] == "BURNED"
            assert db.execute("SELECT active_generation, highest_seen_or_reserved_generation FROM schema_metadata").fetchone() == (0, 2)
        assert not (root / STAGING_ROOT / "tx-m127a").exists()
        return
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    expected_prefix = _expected_committed_prefix(point)
    if point == "BEFORE_INTENT":
        assert not (root / STATE_DB).exists()
        assert not (root / STAGING_ROOT).exists()
        return
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == (1 if expected_prefix else 0)
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == expected_prefix
    if not expected_prefix:
        assert not (root / STAGING_ROOT / "tx-m127a").exists()
        return
    restarted = HostTrustBootstrapFoundation(root, capability=foundation.capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=lambda: "2026-09-03T12:00:00+00:00")
    result = restarted.recover("tx-m127a")
    if point == "AFTER_TERMINAL_COMMIT":
        assert result.state == TrustBootstrapState.ACTIVE.value
        expected_audit = 7
        expected_reservation = "ACTIVE"
        expected_active = 2
    else:
        assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
        expected_audit = expected_prefix + 2 if expected_prefix else 0
        expected_reservation = "BURNED" if expected_prefix else None
        expected_active = 0
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == expected_audit
        assert db.execute("SELECT active_generation, highest_seen_or_reserved_generation FROM schema_metadata").fetchone() == (expected_active, 2 if expected_prefix else 0)
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == (1 if expected_active else 0)
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == (1 if expected_active else 0)
        assert db.execute("SELECT COUNT(*) FROM recovery_observations").fetchone()[0] == (0 if expected_active else 1)
        assert db.execute("SELECT COUNT(*) FROM recovery_verifications").fetchone()[0] == (0 if expected_active else 1)
        if expected_reservation:
            assert db.execute("SELECT reservation_state FROM generation_reservations").fetchone()[0] == expected_reservation
    assert not (root / STAGING_ROOT / "tx-m127a").exists()
    if expected_active == 0:
        for path in OBJECT_PATHS:
            assert not (root / path.lstrip("/")).exists()


def test_recovery_restores_absent_prior_state_with_independent_evidence(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(name):
        if name == "AFTER_ALL_WRITES" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(name)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    result = foundation.recover("tx-m127a")
    assert result.result == "PRIOR_GENERATION_RESTORED_REVIEW_REQUIRED"
    for path in OBJECT_PATHS:
        assert not (root / path.lstrip("/")).exists()
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM recovery_observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM recovery_verifications").fetchone()[0] == 1


@pytest.mark.parametrize("tamper", ["record_json", "record_digest", "previous_record_digest", "journal_head_digest", "remove_audit", "duplicate_audit", "reorder_audit", "metadata_head", "missing_observation", "missing_verification", "observation_digest", "verification_digest", "schema_version", "missing_table", "changed_columns"])
def test_journal_and_schema_corruption_fails_closed(tmp_path, tamper):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        if tamper == "record_digest": db.execute("UPDATE audit SET record_digest=? WHERE sequence=1", ("0" * 64,))
        elif tamper == "record_json": db.execute("UPDATE audit SET record_json=? WHERE sequence=1", (b"{}",))
        elif tamper == "previous_record_digest": db.execute("UPDATE audit SET record_json=replace(record_json, ?, ?) WHERE sequence=2", (b"x", b"y"))
        elif tamper == "journal_head_digest": db.execute("UPDATE audit SET record_json=? WHERE sequence=1", (b"{}",))
        elif tamper == "remove_audit": db.execute("DELETE FROM audit WHERE sequence=3")
        elif tamper == "duplicate_audit": db.execute("UPDATE audit SET sequence=8 WHERE sequence=7")
        elif tamper == "reorder_audit": db.execute("UPDATE audit SET sequence=99 WHERE sequence=1")
        elif tamper == "metadata_head": db.execute("UPDATE schema_metadata SET journal_head_digest=?", ("0" * 64,))
        elif tamper == "missing_observation": db.execute("DELETE FROM observations")
        elif tamper == "missing_verification": db.execute("DELETE FROM verifications")
        elif tamper == "observation_digest": db.execute("UPDATE observations SET record_digest=?", ("0" * 64,))
        elif tamper == "verification_digest": db.execute("UPDATE verifications SET record_digest=?", ("0" * 64,))
        elif tamper == "schema_version": db.execute("UPDATE schema_metadata SET schema_version=99")
        elif tamper == "missing_table": db.execute("DROP TABLE verifications")
        elif tamper == "changed_columns": db.execute("ALTER TABLE audit ADD COLUMN unexpected TEXT")
        db.commit()
    with pytest.raises(HostTrustBootstrapError):
        foundation.recover("tx-m127a")


def _mutate_json_column(db: sqlite3.Connection, table: str, field: str, *, transaction_id: str = "tx-m127a") -> None:
    raw = db.execute(f"SELECT record_json FROM {table} WHERE transaction_id=?", (transaction_id,)).fetchone()[0]
    value = json.loads(raw)
    original = value[field]
    value[field] = "0" * 64 if isinstance(original, str) else (original + 1 if isinstance(original, int) else "changed")
    changed = _raw(value)
    assert changed != raw and json.loads(changed)[field] != original
    db.execute(f"UPDATE {table} SET record_json=? WHERE transaction_id=?", (changed, transaction_id))


@pytest.mark.parametrize("table,field", [
    ("observations", "objects"), ("observations", "observation_digest"),
    ("verifications", "verdict"), ("verifications", "verification_digest"),
])
def test_each_terminal_evidence_json_field_corruption_targets_intended_table(tmp_path, table, field):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        if field.endswith("digest"):
            raw = db.execute(f"SELECT record_json FROM {table} WHERE transaction_id=?", ("tx-m127a",)).fetchone()[0]
            value = json.loads(raw)
            value[field] = "0" * 64
            changed = _raw(value)
            assert json.loads(changed)[field] == "0" * 64
            db.execute(f"UPDATE {table} SET record_json=? WHERE transaction_id=?", (changed, "tx-m127a"))
        else:
            _mutate_json_column(db, table, field)
        db.commit()
    with pytest.raises(HostTrustBootstrapError):
        foundation.recover("tx-m127a")


@pytest.mark.parametrize("field", [
    "transaction_id", "nonce", "trust_generation", "minimum_accepted_generation", "verification_context_digest",
])
def test_current_transaction_canonical_field_corruption_fails_closed(tmp_path, field):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        raw = db.execute("SELECT record_json FROM transactions WHERE transaction_id=?", ("tx-m127a",)).fetchone()[0]
        value = json.loads(raw)
        original = value[field]
        value[field] = 99 if isinstance(original, int) else ("changed-transaction" if field == "transaction_id" else "0" * 64)
        changed = _raw(value)
        assert json.loads(changed)[field] != original
        db.execute("UPDATE transactions SET record_json=? WHERE transaction_id=?", (changed, "tx-m127a"))
        db.commit()
    with pytest.raises(HostTrustBootstrapError):
        foundation.recover("tx-m127a")


@pytest.mark.parametrize("field", ["previous_record_digest", "journal_head_digest"])
def test_audit_canonical_link_corruption_fails_closed(tmp_path, field):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        raw = db.execute("SELECT record_json FROM audit WHERE sequence=2").fetchone()[0]
        value = json.loads(raw)
        value[field] = "0" * 64
        changed = _raw(value)
        assert json.loads(changed)[field] == "0" * 64
        db.execute("UPDATE audit SET record_json=? WHERE sequence=2", (changed,))
        db.commit()
    with pytest.raises(HostTrustBootstrapError):
        foundation.recover("tx-m127a")


@pytest.mark.parametrize("field", ["active_generation", "highest_seen_or_reserved_generation", "minimum_accepted_generation"])
def test_generation_metadata_corruption_is_named_and_fail_closed(tmp_path, field):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        before = db.execute(f"SELECT {field} FROM schema_metadata WHERE singleton=1").fetchone()[0]
        db.execute(f"UPDATE schema_metadata SET {field}=? WHERE singleton=1", (before + 1,))
        after = db.execute(f"SELECT {field} FROM schema_metadata WHERE singleton=1").fetchone()[0]
        assert after == before + 1
        db.commit()
    with pytest.raises(HostTrustBootstrapError):
        foundation.recover("tx-m127a")


def test_recovery_evidence_bytes_and_digest_corruption_are_independent(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_ALL_WRITES" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    foundation.recover("tx-m127a")
    for table, field in (("recovery_observations", "objects"), ("recovery_observations", "observation_digest"), ("recovery_verifications", "verdict"), ("recovery_verifications", "verification_digest")):
        with sqlite3.connect(root / STATE_DB) as db:
            raw = db.execute(f"SELECT record_json FROM {table} WHERE transaction_id=?", ("tx-m127a",)).fetchone()[0]
            value = json.loads(raw)
            value[field] = "0" * 64 if field.endswith("digest") else ("RESTORE_VERIFICATION_FAILED" if field == "verdict" else [{"path": "/wrong"}])
            changed = _raw(value)
            assert json.loads(changed)[field] != json.loads(raw)[field]
            db.execute(f"UPDATE {table} SET record_json=? WHERE transaction_id=?", (changed, "tx-m127a"))
            db.commit()
        with pytest.raises(HostTrustBootstrapError):
            foundation.recover("tx-m127a")
        with sqlite3.connect(root / STATE_DB) as db:
            db.execute(f"UPDATE {table} SET record_json=? WHERE transaction_id=?", (raw, "tx-m127a"))
            db.commit()


def test_staging_ambiguity_and_filesystem_matrix_fail_closed(tmp_path):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    staging = root / STAGING_ROOT / "tx-m127a"
    staging.mkdir(parents=True)
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])

    root2, foundation2 = _foundation(tmp_path, context)
    target = root2 / "etc/aether"
    target.mkdir(parents=True)
    (target / "release-trust-anchor.pub").symlink_to(Path("/etc/passwd"))
    with pytest.raises(HostTrustBootstrapError):
        foundation2.bootstrap(_authorization(context), _fixtures()["objects"])

    root3, foundation3 = _foundation(tmp_path, context)
    current = root3 / OBJECT_PATHS[0].lstrip("/")
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_bytes(b"hard-linked\n")
    os.chmod(current, 0o444)
    os.link(current, current.with_name("anchor-alias"))
    with pytest.raises(HostTrustBootstrapError):
        foundation3.bootstrap(_authorization(context), _fixtures()["objects"])

    root4, foundation4 = _foundation(tmp_path, context)
    fifo = root4 / OBJECT_PATHS[0].lstrip("/")
    fifo.parent.mkdir(parents=True, exist_ok=True)
    os.mkfifo(fifo)
    with pytest.raises(HostTrustBootstrapError):
        foundation4.bootstrap(_authorization(context), _fixtures()["objects"])

    root5, foundation5 = _foundation(tmp_path, context)
    target = root5 / "etc/aether"
    target.mkdir(parents=True)
    (target / ".release-trust-anchor.pub.tmp").write_bytes(b"ambiguous")
    with pytest.raises(HostTrustBootstrapError):
        foundation5.bootstrap(_authorization(context), _fixtures()["objects"])


@pytest.mark.parametrize("mutation", ["wrong_mode", "hard_link", "changed_bytes", "missing", "extra"])
def test_each_staged_identity_condition_reaches_its_named_rejection(tmp_path, mutation):
    context = _context()
    holder: dict[str, Path] = {}
    def fault(point):
        if point != "DURING_STAGE_0":
            return
        staged = holder["root"] / STAGING_ROOT / "tx-m127a" / "00.object"
        if mutation == "wrong_mode":
            os.chmod(staged, 0o555)
        elif mutation == "hard_link":
            os.link(staged, staged.with_name("staged-alias"))
        elif mutation == "changed_bytes":
            staged.write_bytes(b"changed-staged-bytes\n")
        elif mutation == "missing":
            staged.unlink()
        elif mutation == "extra":
            (staged.parent / "unexpected").write_bytes(b"unexpected")
    root, foundation = _foundation(tmp_path, context, fault=fault)
    holder["root"] = root
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    assert not (root / STATE_DB).exists() or (root / STATE_DB).is_file()


@pytest.mark.parametrize("entry", ["root", "state_directory", "database", "lock", "object_parent", "object_target"])
def test_each_symlink_identity_boundary_is_independent(tmp_path, entry):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    outside = tmp_path / f"outside-{entry}"
    outside.mkdir()
    if entry == "root":
        root_alias = tmp_path / "root-alias"
        root_alias.symlink_to(root, target_is_directory=True)
        with pytest.raises(HostTrustBootstrapError):
            HostTrustBootstrapFoundation(root_alias, capability=foundation.capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64)
        return
    if entry == "state_directory":
        (root / "var/lib/aether").mkdir(parents=True)
        (root / "var/lib/aether/trust-bootstrap").symlink_to(outside, target_is_directory=True)
    elif entry == "database":
        (root / "var/lib/aether/trust-bootstrap").mkdir(parents=True)
        (root / STATE_DB).symlink_to(outside / "database")
    elif entry == "lock":
        (root / "var/lib/aether/trust-bootstrap").mkdir(parents=True)
        (root / "var/lib/aether/trust-bootstrap/state.lock").symlink_to(outside / "lock")
    elif entry == "object_parent":
        (root / "etc").mkdir()
        (root / "etc/aether").symlink_to(outside, target_is_directory=True)
    else:
        target = root / OBJECT_PATHS[0].lstrip("/")
        target.parent.mkdir(parents=True)
        target.symlink_to(outside / "target")
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])


def test_current_and_retained_hard_link_and_mode_identity_are_independent(tmp_path):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    current = root / OBJECT_PATHS[0].lstrip("/")
    current.parent.mkdir(parents=True)
    current.write_bytes(b"prior\n")
    os.chmod(current, 0o444)
    os.link(current, current.with_name("current-alias"))
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])

    root_mode, foundation_mode = _foundation(tmp_path, context)
    mode_target = root_mode / OBJECT_PATHS[0].lstrip("/")
    mode_target.parent.mkdir(parents=True)
    mode_target.write_bytes(b"prior-mode\n")
    os.chmod(mode_target, 0o555)
    with pytest.raises(HostTrustBootstrapError):
        foundation_mode.bootstrap(_authorization(context), _fixtures()["objects"])

    fired = {"value": False}
    def interrupt(point):
        if point == "AFTER_ALL_WRITES" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root2, foundation2 = _foundation(tmp_path, context, fault=interrupt)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation2.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root2 / STATE_DB) as db:
        prior = b"retained-prior\n"
        db.execute("UPDATE prior_objects SET present=1, mode=?, owner_model='CURRENT_USER', group_model='CURRENT_GROUP', link_count=1, link_identity=?, content=?, content_digest=? WHERE path=?", (0o555, "1" * 64, prior, hashlib.sha256(prior).hexdigest(), OBJECT_PATHS[0]))
        db.commit()
    result = foundation2.recover("tx-m127a")
    assert result.state == TrustBootstrapState.REVIEW_REQUIRED.value
    assert result.result == "ROOT_REVIEW_REQUIRED"

    fired3 = {"value": False}
    def interrupt3(point):
        if point == "AFTER_ALL_WRITES" and not fired3["value"]:
            fired3["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root3, foundation3 = _foundation(tmp_path, context, fault=interrupt3)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation3.bootstrap(_authorization(context), _fixtures()["objects"])
    with sqlite3.connect(root3 / STATE_DB) as db:
        prior = b"retained-link\n"
        db.execute("UPDATE prior_objects SET present=1, mode=?, owner_model='CURRENT_USER', group_model='CURRENT_GROUP', link_count=2, link_identity=?, content=?, content_digest=? WHERE path=?", (0o444, "2" * 64, prior, hashlib.sha256(prior).hexdigest(), OBJECT_PATHS[0]))
        db.commit()
    link_result = foundation3.recover("tx-m127a")
    assert link_result.state == TrustBootstrapState.REVIEW_REQUIRED.value
    assert link_result.result == "ROOT_REVIEW_REQUIRED"


def test_fifo_non_regular_and_publication_temporary_path_are_rejected_separately(tmp_path):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    fifo = root / OBJECT_PATHS[0].lstrip("/")
    fifo.parent.mkdir(parents=True)
    os.mkfifo(fifo)
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])

    root2, foundation2 = _foundation(tmp_path, context)
    temporary = root2 / "etc/aether/.release-trust-anchor.pub.tmp"
    temporary.parent.mkdir(parents=True)
    temporary.write_bytes(b"ambiguous")
    with pytest.raises(HostTrustBootstrapError):
        foundation2.bootstrap(_authorization(context), _fixtures()["objects"])


@pytest.mark.parametrize("mutation", ["missing", "extra", "alternate", "traversal", "oversized", "changed_verifier", "changed_verifier_digest"])
def test_object_scope_and_content_matrix_fails_before_intent(tmp_path, mutation):
    context = _context()
    root, foundation = _foundation(tmp_path, context)
    objects = dict(_fixtures()["objects"])
    if mutation == "missing":
        objects.pop(OBJECT_PATHS[0])
    elif mutation == "extra":
        objects["/etc/aether/extra"] = b"extra"
    elif mutation == "alternate":
        objects["/etc/aether/release-trust-anchor.pub.alternate"] = objects[OBJECT_PATHS[0]]
    elif mutation == "traversal":
        objects["../escape"] = objects.pop(OBJECT_PATHS[0])
    elif mutation == "oversized":
        objects[OBJECT_PATHS[4]] = b"x" * (1024 * 1024 + 1)
    elif mutation == "changed_verifier":
        objects[OBJECT_PATHS[4]] = b"changed-verifier\n"
    else:
        objects[OBJECT_PATHS[3]] = ("0" * 64 + "\n").encode("ascii")
    with pytest.raises(HostTrustBootstrapError):
        foundation.bootstrap(_authorization(context), objects)
    assert not (root / STATE_DB).exists()


def test_concurrency_recovery_and_lock_timeout_are_serialized(tmp_path):
    context = _context()
    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="tx-m127a")
    def run():
        foundation = HostTrustBootstrapFoundation(root, capability=capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=lambda: "2026-09-03T12:00:00+00:00")
        return foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert results[0] == results[1]
    lock_stream = (root / "var/lib/aether/trust-bootstrap/state.lock").open("a+b")
    try:
        import fcntl
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        blocked = HostTrustBootstrapFoundation(root, capability=capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, lock_timeout_seconds=0.01)
        with pytest.raises(HostTrustBootstrapError):
            blocked.recover("tx-m127a")
    finally:
        lock_stream.close()


def _raw_bootstrap_kwargs(objects=None, *, payload=None, envelope=None, allow_expired=False):
    fixture = _fixtures()
    return {
        "authority_raw": fixture["authority_raw"], "authority_signature": BASELINE_SIG,
        "local_console_raw": fixture["local_raw"], "local_console_signature": LOCAL_SIG,
        "governance_raw": fixture["governance_raw"], "governance_signature": GOVERNANCE_SIG,
        "payload_raw": payload or fixture["payload_raw"], "envelope_raw": envelope or fixture["envelope_raw"],
        "objects": objects or fixture["objects"], "allow_expired_existing": allow_expired,
        "verification_time_utc": "2026-09-03T12:00:00+00:00",
    }


def _concurrent_foundation(root, capability, context, *, now="2026-09-03T12:00:00+00:00"):
    return HostTrustBootstrapFoundation(root, capability=capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, now_utc=lambda: now)


def _ordered_valid_competition(tmp_path: Path, winner: VerifiedAuthorization, loser: VerifiedAuthorization, winner_objects: dict[str, bytes], loser_objects: dict[str, bytes]):
    context = winner.context
    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id=winner.payload["transaction_id"])
    winner_foundation = _concurrent_foundation(root, capability, context)
    loser_ready = threading.Event()
    winner_done = threading.Event()

    def loser_fault(point: str) -> None:
        if point == "BEFORE_INTENT":
            loser_ready.set()
            winner_done.wait()

    loser_foundation = HostTrustBootstrapFoundation(
        root,
        capability=capability,
        context=context,
        authorization_verifier=AuthorizationVerifier(context),
        target_host_identity_digest="2" * 64,
        target_boot_digest="3" * 64,
        fault_injector=loser_fault,
        now_utc=lambda: "2026-09-03T12:00:00+00:00",
    )

    def run_loser():
        try:
            return loser_foundation.bootstrap(loser, loser_objects)
        except HostTrustBootstrapError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        loser_future = pool.submit(run_loser)
        loser_ready.wait()
        winner_future = pool.submit(winner_foundation.bootstrap, winner, winner_objects)
        try:
            winner_result = winner_future.result()
        finally:
            winner_done.set()
        loser_result = loser_future.result()
    return root, winner_result, loser_result


def test_concurrency_identical_transaction_uses_separate_foundations_and_one_commit(tmp_path):
    context = _context()
    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="tx-m127a")
    def run():
        return _concurrent_foundation(root, capability, context).bootstrap(_authorization(context), _fixtures()["objects"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert results[0].state == results[1].state == TrustBootstrapState.ACTIVE.value
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(DISTINCT nonce), COUNT(DISTINCT trust_generation) FROM transactions").fetchone() == (1, 1)
        assert db.execute("SELECT active_generation, highest_seen_or_reserved_generation FROM schema_metadata").fetchone() == (2, 2)


@pytest.mark.parametrize("conflict", ["payload", "envelope", "object_bytes"])
def test_concurrency_same_transaction_conflicts_have_one_exact_winner(tmp_path, conflict):
    context = _context()
    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="tx-m127a")
    fixture = _fixtures()
    payload = fixture["payload_raw"]
    envelope = fixture["envelope_raw"]
    objects = fixture["objects"]
    if conflict == "payload":
        value = json.loads(payload)
        value["nonce"] = "conflicting-nonce"
        payload = _raw(value)
    elif conflict == "envelope":
        value = json.loads(envelope)
        value["domain_separator"] = "changed.domain"
        envelope = _raw(value)
    else:
        objects = dict(objects)
        objects[OBJECT_PATHS[4]] = b"different-object\n"
    valid_foundation = _concurrent_foundation(root, capability, context)
    invalid_foundation = _concurrent_foundation(root, capability, context)
    valid_kwargs = _raw_bootstrap_kwargs()
    invalid_kwargs = _raw_bootstrap_kwargs(objects=objects, payload=payload, envelope=envelope)
    def valid():
        return valid_foundation.bootstrap_from_raw(**valid_kwargs)
    def invalid():
        try:
            invalid_foundation.bootstrap_from_raw(**invalid_kwargs)
        except HostTrustBootstrapError as exc:
            return type(exc).__name__
        return "UNEXPECTED_SUCCESS"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [future.result() for future in (pool.submit(valid), pool.submit(invalid))]
    assert results[0].state == TrustBootstrapState.ACTIVE.value
    assert results[1] == "HostTrustBootstrapError"
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1


def test_concurrency_resume_and_two_recovery_callers_have_one_terminal_review(tmp_path):
    context = _context()
    fired = {"value": False}
    def fault(point):
        if point == "AFTER_TRUST_BOOTSTRAP_REQUESTED" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)
    root, foundation = _foundation(tmp_path, context, fault=fault)
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(_authorization(context), _fixtures()["objects"])
    callers = [_concurrent_foundation(root, foundation.capability, context) for _ in range(3)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda item: item.recover("tx-m127a"), callers))
    assert all(result.state == TrustBootstrapState.REVIEW_REQUIRED.value for result in results)
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM recovery_observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM recovery_verifications").fetchone()[0] == 1
        assert db.execute("SELECT active_generation, highest_seen_or_reserved_generation FROM schema_metadata").fetchone() == (0, 2)


def test_valid_same_nonce_competition_arbitrates_after_both_authorizations_verify(tmp_path):
    bundle = _signed_valid_fixture_bundle(tmp_path, [
        {"name": "winner", "authorization_id": "valid-auth-winner", "transaction_id": "valid-tx-winner", "nonce": "shared-valid-nonce", "trust_generation": 2, "minimum_accepted_generation": 1},
        {"name": "loser", "authorization_id": "valid-auth-loser", "transaction_id": "valid-tx-loser", "nonce": "shared-valid-nonce", "trust_generation": 3, "minimum_accepted_generation": 2},
    ])
    winner = _dynamic_authorization(bundle, "winner")
    loser = _dynamic_authorization(bundle, "loser")
    assert winner.payload["nonce"] == loser.payload["nonce"]
    assert winner.payload["transaction_id"] != loser.payload["transaction_id"]
    assert winner.payload["trust_generation"] != loser.payload["trust_generation"]

    root, winner_result, loser_result = _ordered_valid_competition(
        tmp_path,
        winner,
        loser,
        bundle["cases"]["winner"]["objects"],
        bundle["cases"]["loser"]["objects"],
    )
    assert winner_result.state == TrustBootstrapState.ACTIVE.value
    assert isinstance(loser_result, HostTrustBootstrapError)
    assert "nonce or generation conflicts" in str(loser_result)
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM generation_reservations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM prior_objects").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1
        assert db.execute("SELECT transaction_id, nonce, trust_generation FROM transactions").fetchone() == ("valid-tx-winner", "shared-valid-nonce", 2)
        assert db.execute("SELECT transaction_id, reservation_state FROM generation_reservations").fetchone() == ("valid-tx-winner", "ACTIVE")
        assert db.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata").fetchone() == (1, 2, 2)
    assert not (root / STAGING_ROOT / "valid-tx-loser").exists()
    for path, data in bundle["cases"]["winner"]["objects"].items():
        assert (root / path.lstrip("/")).read_bytes() == data


def test_valid_same_generation_competition_reserves_one_generation(tmp_path):
    bundle = _signed_valid_fixture_bundle(tmp_path, [
        {"name": "winner", "authorization_id": "valid-auth-generation-winner", "transaction_id": "valid-tx-generation-winner", "nonce": "valid-generation-nonce-a", "trust_generation": 2, "minimum_accepted_generation": 1},
        {"name": "loser", "authorization_id": "valid-auth-generation-loser", "transaction_id": "valid-tx-generation-loser", "nonce": "valid-generation-nonce-b", "trust_generation": 2, "minimum_accepted_generation": 1},
    ])
    winner = _dynamic_authorization(bundle, "winner")
    loser = _dynamic_authorization(bundle, "loser")
    assert winner.payload["trust_generation"] == loser.payload["trust_generation"]
    assert winner.payload["nonce"] != loser.payload["nonce"]

    root, winner_result, loser_result = _ordered_valid_competition(
        tmp_path,
        winner,
        loser,
        bundle["cases"]["winner"]["objects"],
        bundle["cases"]["loser"]["objects"],
    )
    assert winner_result.state == TrustBootstrapState.ACTIVE.value
    assert isinstance(loser_result, HostTrustBootstrapError)
    assert "trust generation is stale" in str(loser_result)
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM generation_reservations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1
        assert db.execute("SELECT transaction_id, nonce, trust_generation FROM transactions").fetchone() == ("valid-tx-generation-winner", "valid-generation-nonce-a", 2)
        assert db.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata").fetchone() == (1, 2, 2)
    assert not (root / STAGING_ROOT / "valid-tx-generation-loser").exists()


def test_valid_lower_then_higher_generation_preserves_history_and_advances_active_set(tmp_path):
    bundle = _signed_valid_fixture_bundle(tmp_path, [
        {"name": "lower", "authorization_id": "valid-auth-lower", "transaction_id": "valid-tx-lower", "nonce": "valid-lower-nonce", "trust_generation": 2, "minimum_accepted_generation": 1},
        {"name": "higher", "authorization_id": "valid-auth-higher", "transaction_id": "valid-tx-higher", "nonce": "valid-higher-nonce", "trust_generation": 3, "minimum_accepted_generation": 2},
    ])
    context = bundle["context"]
    lower = _dynamic_authorization(bundle, "lower")
    higher = _dynamic_authorization(bundle, "higher")
    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="valid-tx-lower")
    foundation = _concurrent_foundation(root, capability, context)
    assert foundation.bootstrap(lower, bundle["cases"]["lower"]["objects"]).state == TrustBootstrapState.ACTIVE.value
    assert foundation.bootstrap(higher, bundle["cases"]["higher"]["objects"]).state == TrustBootstrapState.ACTIVE.value
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 14
        assert db.execute("SELECT COUNT(*) FROM prior_objects").fetchone()[0] == 10
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 2
        assert db.execute("SELECT transaction_id, reservation_state FROM generation_reservations ORDER BY trust_generation").fetchall() == [("valid-tx-lower", "ACTIVE"), ("valid-tx-higher", "ACTIVE")]
        assert db.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata").fetchone() == (2, 3, 3)
        assert db.execute("SELECT DISTINCT transaction_id FROM audit ORDER BY transaction_id").fetchall() == [("valid-tx-higher",), ("valid-tx-lower",)]
    for path, data in bundle["cases"]["higher"]["objects"].items():
        assert (root / path.lstrip("/")).read_bytes() == data
    assert not (root / STAGING_ROOT / "valid-tx-lower").exists()
    assert not (root / STAGING_ROOT / "valid-tx-higher").exists()


def test_valid_higher_then_lower_generation_is_stale_without_intent_or_regression(tmp_path):
    bundle = _signed_valid_fixture_bundle(tmp_path, [
        {"name": "higher", "authorization_id": "valid-auth-high-first", "transaction_id": "valid-tx-high-first", "nonce": "valid-high-first-nonce", "trust_generation": 3, "minimum_accepted_generation": 2},
        {"name": "lower", "authorization_id": "valid-auth-low-second", "transaction_id": "valid-tx-low-second", "nonce": "valid-low-second-nonce", "trust_generation": 2, "minimum_accepted_generation": 1},
    ])
    context = bundle["context"]
    higher = _dynamic_authorization(bundle, "higher")
    lower = _dynamic_authorization(bundle, "lower")
    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="valid-tx-high-first")
    foundation = _concurrent_foundation(root, capability, context)
    assert foundation.bootstrap(higher, bundle["cases"]["higher"]["objects"]).state == TrustBootstrapState.ACTIVE.value
    with pytest.raises(HostTrustBootstrapError, match="trust generation is stale"):
        foundation.bootstrap(lower, bundle["cases"]["lower"]["objects"])
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 7
        assert db.execute("SELECT COUNT(*) FROM generation_reservations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM prior_objects").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1
        assert db.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata").fetchone() == (2, 3, 3)
    for path, data in bundle["cases"]["higher"]["objects"].items():
        assert (root / path.lstrip("/")).read_bytes() == data
    assert not (root / STAGING_ROOT / "valid-tx-low-second").exists()


def test_valid_burned_generation_cannot_be_reused_before_later_generation_activates(tmp_path):
    bundle = _signed_valid_fixture_bundle(tmp_path, [
        {"name": "burn", "authorization_id": "valid-auth-burn", "transaction_id": "valid-tx-burn", "nonce": "valid-burn-nonce", "trust_generation": 2, "minimum_accepted_generation": 1},
        {"name": "burn-retry", "authorization_id": "valid-auth-burn-retry", "transaction_id": "valid-tx-burn-retry", "nonce": "valid-burn-retry-nonce", "trust_generation": 2, "minimum_accepted_generation": 1},
        {"name": "later", "authorization_id": "valid-auth-later", "transaction_id": "valid-tx-later", "nonce": "valid-later-nonce", "trust_generation": 3, "minimum_accepted_generation": 2},
    ])
    context = bundle["context"]
    burned = _dynamic_authorization(bundle, "burn")
    burned_retry = _dynamic_authorization(bundle, "burn-retry")
    later = _dynamic_authorization(bundle, "later")
    fired = {"value": False}

    def interrupt(point: str) -> None:
        if point == "AFTER_TRUST_BOOTSTRAP_REQUESTED" and not fired["value"]:
            fired["value"] = True
            raise HostTrustBootstrapInterrupted(point)

    root, capability = create_isolated_root(tmp_path, purpose="M127A_BOOTSTRAP", transaction_id="valid-tx-burn")
    foundation = HostTrustBootstrapFoundation(root, capability=capability, context=context, authorization_verifier=AuthorizationVerifier(context), target_host_identity_digest="2" * 64, target_boot_digest="3" * 64, fault_injector=interrupt, now_utc=lambda: "2026-09-03T12:00:00+00:00")
    with pytest.raises(HostTrustBootstrapInterrupted):
        foundation.bootstrap(burned, bundle["cases"]["burn"]["objects"])
    assert foundation.recover("valid-tx-burn").state == TrustBootstrapState.REVIEW_REQUIRED.value
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT transaction_id, reservation_state FROM generation_reservations").fetchone() == ("valid-tx-burn", "BURNED")
        assert db.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata").fetchone() == (1, 2, 0)
    with pytest.raises(HostTrustBootstrapError, match="trust generation is stale"):
        foundation.bootstrap(burned_retry, bundle["cases"]["burn-retry"]["objects"])
    assert foundation.bootstrap(later, bundle["cases"]["later"]["objects"]).state == TrustBootstrapState.ACTIVE.value
    with sqlite3.connect(root / STATE_DB) as db:
        assert db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 10
        assert db.execute("SELECT COUNT(*) FROM prior_objects").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM verifications").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM recovery_observations").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM recovery_verifications").fetchone()[0] == 1
        assert db.execute("SELECT trust_generation, transaction_id, reservation_state FROM generation_reservations ORDER BY trust_generation").fetchall() == [(2, "valid-tx-burn", "BURNED"), (3, "valid-tx-later", "ACTIVE")]
        assert db.execute("SELECT minimum_accepted_generation, highest_seen_or_reserved_generation, active_generation FROM schema_metadata").fetchone() == (2, 3, 3)
    for path, data in bundle["cases"]["later"]["objects"].items():
        assert (root / path.lstrip("/")).read_bytes() == data
    assert not (root / STAGING_ROOT / "valid-tx-burn-retry").exists()
    assert not (root / STAGING_ROOT / "valid-tx-later").exists()
