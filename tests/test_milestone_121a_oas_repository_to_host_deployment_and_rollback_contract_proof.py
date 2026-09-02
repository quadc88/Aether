"""Semantic static proof lock for the corrected M121A deployment contract."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / (
    "docs/architecture/"
    "MILESTONE_121A_OAS_REPOSITORY_TO_HOST_DEPLOYMENT_AND_ROLLBACK_CONTRACT_PROOF.md"
)

EXPECTED_STATES = {
    "NO_DEPLOYMENT",
    "CANDIDATE_PENDING",
    "QUIESCE_REQUIRED",
    "ACTIVATING",
    "COMMITTED",
    "ROLLBACK_PENDING",
    "RECOVERY_REQUIRED",
}


def _text() -> str:
    return PROOF.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def _tail(text: str, heading: str) -> str:
    return text[text.index(heading) :]


def _require(text: str, *values: str) -> None:
    for value in values:
        assert value in text, value


def _tables(section: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    lines = section.splitlines()
    result: list[tuple[list[str], list[dict[str, str]]]] = []
    index = 0
    while index < len(lines):
        if not lines[index].startswith("|"):
            index += 1
            continue
        table_lines: list[str] = []
        while index < len(lines) and lines[index].startswith("|"):
            table_lines.append(lines[index])
            index += 1
        if len(table_lines) < 2:
            continue
        header = _cells(table_lines[0])
        body = [
            _cells(line)
            for line in table_lines[1:]
            if not re.fullmatch(r"\|\s*:?-+:?(?:\s*\|\s*:?-+:?)+\s*\|?", line)
        ]
        if body:
            result.append((header, [dict(zip(header, row)) for row in body]))
    return result


def _cells(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def _table(section: str, header: list[str]) -> list[dict[str, str]]:
    for actual, rows in _tables(section):
        if actual == header:
            return rows
    raise AssertionError(f"missing table: {header}")


def _code_blocks(text: str) -> list[str]:
    return re.findall(r"```(?:text)?\n(.*?)```", text, flags=re.DOTALL)


def _status_block(text: str) -> dict[str, str]:
    matches = re.findall(
        r"AUTHORITATIVE_M121A_STATUS_BEGIN\n(.*?)\nAUTHORITATIVE_M121A_STATUS_END",
        text,
        flags=re.DOTALL,
    )
    assert len(matches) == 1
    values: dict[str, str] = {}
    for line in matches[0].splitlines():
        key, separator, value = line.partition(": ")
        if separator:
            assert key not in values, key
            values[key] = value
    return values


def _unit_block(text: str) -> str:
    for block in _code_blocks(text):
        if "[Unit]" in block and "LimitNOFILE=512" in block:
            return block
    raise AssertionError("exact service unit block is missing")


UNIT_DIRECTIVES = {
    "Unit": {
        "Description",
        "Requires",
        "After",
        "ConditionPathExists",
        "AssertPathExists",
        "StartLimitIntervalSec",
        "StartLimitBurst",
        "StartLimitAction",
    },
    "Service": {
        "Sockets",
        "User",
        "Group",
        "SupplementaryGroups",
        "ExecStart",
        "WorkingDirectory",
        "Environment",
        "UMask",
        "Type",
        "NotifyAccess",
        "NoNewPrivileges",
        "PrivateTmp",
        "PrivateDevices",
        "ProtectSystem",
        "ProtectHome",
        "ReadOnlyPaths",
        "ReadWritePaths",
        "RestrictAddressFamilies",
        "RestrictSUIDSGID",
        "CapabilityBoundingSet",
        "AmbientCapabilities",
        "LockPersonality",
        "ProtectKernelTunables",
        "ProtectKernelModules",
        "ProtectKernelLogs",
        "ProtectControlGroups",
        "ProtectClock",
        "RestrictNamespaces",
        "RestrictRealtime",
        "SystemCallArchitectures",
        "LimitCORE",
        "LimitNOFILE",
        "FileDescriptorStoreMax",
        "TasksMax",
        "MemoryMax",
        "CPUQuota",
        "Restart",
        "RestartSec",
        "TimeoutStartSec",
        "TimeoutStopSec",
        "StandardOutput",
        "StandardError",
    },
    "Install": set(),
}


def _parse_service_unit(text: str) -> dict[str, list[tuple[str, str]]]:
    sections: dict[str, list[tuple[str, str]]] = {}
    current: str | None = None
    for line in _unit_block(text).splitlines():
        if not line.strip():
            continue
        if line.startswith("["):
            assert line.endswith("]")
            current = line[1:-1]
            assert current in UNIT_DIRECTIVES, current
            assert current not in sections, current
            sections[current] = []
            continue
        assert current is not None
        assert "=" in line, line
        key, value = line.split("=", 1)
        assert key in UNIT_DIRECTIVES[current], (current, key)
        sections[current].append((key, value))
    assert set(sections) == set(UNIT_DIRECTIVES)
    for section, entries in sections.items():
        values_by_key: dict[str, list[str]] = {}
        for key, value in entries:
            values_by_key.setdefault(key, []).append(value)
        for key, values in values_by_key.items():
            if key not in {"Environment", "ConditionPathExists"}:
                assert len(values) == 1, (section, key)
        if "Environment" in values_by_key:
            names = [value.split("=", 1)[0] for value in values_by_key["Environment"]]
            assert len(names) == len(set(names))
        if "ConditionPathExists" in values_by_key:
            assert len(values_by_key["ConditionPathExists"]) == len(
                set(values_by_key["ConditionPathExists"])
            )
    return sections


def test_record_structure_and_authority_are_unique():
    text = _text()
    assert PROOF.is_file()
    headings = re.findall(r"^#{2} .+$", text, flags=re.MULTILINE)
    expected = [f"{number}." for number in range(1, 16)]
    assert [heading.split()[1] for heading in headings] == expected
    _require(
        _normalized(text),
        "PM disposition: `RETURN_M121A_FOR_SECOND_CORRECTION`",
        "CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION",
        "Aether is one persistent digital mind",
        "OAS is a bounded authority service, not another mind, agent, or cognitive runtime",
        "Only these two repository artifacts are in scope for the corrective pass",
        "No existing repository file is modified",
    )
    assert text.count("AUTHORITATIVE_M121A_STATUS_BEGIN") == 1
    assert text.count("AUTHORITATIVE_M121A_STATUS_END") == 1
    assert len(text.splitlines()) >= 900


def test_pm_hard_gate_matrix_has_all_gates_closed_by_design():
    section = _section(text := _text(), "## 3. Corrective Hard-Gate Closure Matrix", "## 4. Activation Identity State Machine")
    rows = _table(
        section,
        [
            "Gate",
            "Required invariant",
            "Design owner",
            "Static structure",
            "Runtime/deployment status",
            "Result",
        ],
    )
    assert [row["Gate"].split()[0] for row in rows] == list("ABCDEFG")
    assert all(row["Result"] == "CLOSED_BY_DESIGN" for row in rows)
    assert all(row["Runtime/deployment status"] in {"Not implemented; not deployed", "Not implemented as units; not deployed", "No verifier or key exists on target", "Entrypoint not implemented", "Units not implemented", "Build not authorized"} for row in rows)
    _require(text, "The static proof parses the structured tables and rejects contradictory values")


def test_activation_record_and_transitions_are_complete_and_non_circular():
    text = _text()
    state_section = _section(text, "## 4. Activation Identity State Machine", "## 5. Release Identity and Signing Trust Root")
    state_blocks = [
        set(block.splitlines()) & EXPECTED_STATES
        for block in _code_blocks(state_section)
        if EXPECTED_STATES & set(block.splitlines())
    ]
    assert EXPECTED_STATES in state_blocks
    field_rows = _table(
        state_section,
        ["Field", "Serialization and meaning"],
    )
    required_fields = {
        "record_version",
        "state",
        "transaction_id",
        "record_sequence",
        "previous_record_digest",
        "host_boot_id",
        "activation_issued_at_monotonic",
        "activation_expires_at_monotonic",
        "activation_max_duration_seconds",
        "old_release_id",
        "old_manifest_digest",
        "candidate_release_id",
        "candidate_manifest_digest",
        "current_link_release_id",
        "old_unit_generation_id",
        "candidate_unit_generation_id",
        "unit_bundle_digest",
        "quiesce_state",
        "schema_before",
        "schema_after",
        "schema_compatibility",
        "migration_state",
        "readiness_result",
        "smoke_result",
        "commit_state",
        "rollback_state",
        "activation_reason",
        "created_at_utc` / `updated_at_utc",
    }
    assert {row["Field"].strip("`") for row in field_rows} == required_fields
    assert "/var/lib/aether/activation/activation-record.json" in state_section
    assert "root-owned regular file, mode `0444`" in state_section
    assert "fsync" in state_section
    assert "There is no second authoritative" in _normalized(state_section)
    assert "active-release identity object" in _normalized(state_section)
    assert "not an independent anti-rollback anchor" in _normalized(state_section)
    assert "malicious root can replace the record" in _normalized(state_section)
    assert "prevents old-record replay" not in state_section

    transitions = _table(state_section, ["From", "To", "Exact guard and mutation"])
    transition_pairs = {(row["From"], row["To"]) for row in transitions}
    assert ("absent record", "`NO_DEPLOYMENT`") in transition_pairs
    assert ("`NO_DEPLOYMENT`", "`CANDIDATE_PENDING`") in transition_pairs
    assert ("`COMMITTED`", "`CANDIDATE_PENDING`") in transition_pairs
    assert ("`CANDIDATE_PENDING`", "`QUIESCE_REQUIRED`") in transition_pairs
    assert ("`QUIESCE_REQUIRED`", "`ACTIVATING`") in transition_pairs
    assert ("`ACTIVATING`", "`COMMITTED`") in transition_pairs
    assert ("`ACTIVATING`", "`ROLLBACK_PENDING`") in transition_pairs
    assert ("`ROLLBACK_PENDING`", "`COMMITTED`") in transition_pairs
    assert ("any pending state", "`RECOVERY_REQUIRED`") in transition_pairs
    assert ("`RECOVERY_REQUIRED`", "`CANDIDATE_PENDING`") in transition_pairs
    assert ("`COMMITTED`", "`ACTIVATING`") not in transition_pairs
    committed = [row for row in transitions if row["To"].strip("`") == "COMMITTED"]
    assert len(committed) == 2
    assert "READY=1" in committed[0]["Exact guard and mutation"]
    assert "readiness/smoke pass" in committed[1]["Exact guard and mutation"]


def test_first_install_upgrade_and_candidate_startup_traces_are_truthful():
    text = _text()
    section = _section(text, "## 4. Activation Identity State Machine", "## 5. Release Identity and Signing Trust Root")
    _require(
        _normalized(section),
        "NO_DEPLOYMENT -> CANDIDATE_PENDING (old release and old generation are null) -> QUIESCE_REQUIRED -> ACTIVATING (candidate generation gate verified; current points to candidate) -> READY=1 (candidate is authorized by the pending record, not committed) -> SMOKE_PASS -> COMMITTED (candidate identity becomes the sole committed identity)",
        "COMMITTED(old) -> CANDIDATE_PENDING(old + candidate) -> QUIESCE_REQUIRED -> ACTIVATING(old + candidate; current points to candidate) -> READY=1 (candidate authorization is pending-record based) -> SMOKE_PASS -> COMMITTED(candidate)",
        "For `CODE_UPGRADE`, `schema_before == schema_after` and migration remains `NOT_STARTED`",
        "For `SCHEMA_UPGRADE`, a protected backup is recorded first",
    )
    startup = next(
        block
        for block in _code_blocks(section)
        if "record.state == ACTIVATING" in block
    )
    predicates = {
        line.strip()
        for line in startup.splitlines()
        if "==" in line or "!= INCOMPATIBLE" in line or "< record." in line
    }
    assert {
        "record.state == ACTIVATING",
        "record.transaction_id == approved transaction",
        "record.host_boot_id == current boot ID",
        "record.activation_issued_at_monotonic < now < record.activation_expires_at_monotonic",
        "record.candidate_release_id == verified current-link release",
        "record.candidate_manifest_digest == verified manifest digest",
        "record.candidate_unit_generation_id == verified unit-generation gate",
        "record.schema_compatibility != INCOMPATIBLE",
        "record.commit_state == UNCOMMITTED",
    } <= predicates
    _require(
        _normalized(section),
        "unrecorded candidate",
            "stale or monotonic-expired window",
        "wrong boot ID",
        "wrong transaction",
        "replayed record digest",
        "mismatched current link",
        "mismatched unit generation",
        "mismatched manifest",
        "incompatible or unexpected schema",
        "simultaneous activation",
        "exits nonzero without `READY=1`",
    )
    assert "UTC is audit metadata" in _normalized(section)
    assert "malicious root can replace the record" in _normalized(section)


def test_every_activation_crash_boundary_has_a_bounded_recovery_result():
    section = _section(_text(), "### 4.6 Crash and power-loss recovery", "## 5. Release Identity and Signing Trust Root")
    rows = _table(section, ["Interruption point", "Durable result", "Boot/recovery result"])
    assert len(rows) == 13
    expected_points = (
        "Before pending record",
        "After pending record, before unit work",
        "During admission/socket/service quiesce",
        "After stop but before quiescence proof",
        "During unit replacement",
        "After complete unit verification, before `ACTIVATING`",
        "After `ACTIVATING`, before current switch",
        "After current switch, before readiness",
        "After migration starts, before migration commit",
        "After readiness/smoke, before commit",
        "After committed record replacement",
        "During rollback",
        "Missing/corrupt record or anchor",
    )
    assert tuple(row["Interruption point"] for row in rows) == expected_points
    assert all(row["Durable result"] and row["Boot/recovery result"] for row in rows)
    _require(
        _normalized(section),
        "Every socket and service Condition fails",
        "old gate and units unchanged",
        "sends the transaction to recovery",
        "no automatic candidate start",
        "root restores old identity or enters recovery",
    )


def test_release_signature_envelope_and_trust_anchor_are_structured():
    text = _text()
    section = _section(text, "## 5. Release Identity and Signing Trust Root", "## 6. Python Runtime, Import Roots, and Environment")
    field_tables = [
        rows for header, rows in _tables(section) if header == ["Field", "Exact contract"]
    ]
    assert len(field_tables) == 2
    envelope, approval_payload = field_tables
    assert {row["Field"].strip("`") for row in envelope} == {
        "envelope_version",
        "domain",
        "manifest_version",
        "manifest_sha256",
        "manifest_length",
        "release_id",
        "approval_payload",
        "release_signature",
        "approval_signature",
        "rotation_signatures",
    }
    assert {row["Field"].strip("`") for row in approval_payload} == {
        "manifest_digest",
        "release_id",
        "source_commit",
        "test_evidence_digest",
        "approval_id",
        "activation_release_policy",
        "issued_at_utc",
        "expires_at_utc",
        "approver_policy",
    }
    anchor = _table(section, ["Lifecycle event", "Exact rule"])
    assert {row["Lifecycle event"] for row in anchor} == {
        "Normal release",
        "Planned rotation",
        "Rotation overlap",
        "Revocation",
        "Compromised key",
        "Rollback",
        "Damaged/missing anchor",
        "Audit",
    }
    _require(
        _normalized(section),
        "SIGNED_BYTES =",
        'ASCII("aether.m121a.release-manifest.v1")',
        "APPROVAL_BYTES =",
        'ASCII("aether.m121a.release-approval.v1")',
        "`signature` decodes to exactly 64 bytes",
        "/etc/aether/release-trust-anchor.pub",
        "anchor_version",
        "anchor_id",
        "keys",
        "rotation_policy",
        "revocations",
        "anchor_fingerprint",
        "/usr/libexec/aether-release-verify",
        "/usr/bin/openssl",
        "OpenSSL 3.0 Ed25519 pkeyutl verification only",
        "ANCHOR_DOMAIN = ASCII(\"aether.m121a.release-trust-anchor.v1\")",
        "ANCHOR_FINGERPRINT = SHA256(ANCHOR_DOMAIN + BYTE(0x00)",
        "never contains `anchor_fingerprint`",
        "approval payload",
        "payload/signature mismatch",
        "wrong test-evidence digest",
        "approval payload digest",
        "`rotation_signatures` is exactly `[]`",
        "exactly one old release signature",
        "one old approval signature",
        "four signatures",
        "conflicting validity windows",
        "/var/lib/aether/install/<tx>/verify/release-signed-bytes.bin",
        "/var/lib/aether/install/<tx>/verify/approval-key.spki.der",
        "execve",
        "-rawin",
        "-sigfile",
        "-keyform",
        "DER",
        "no caller environment",
        "Signature Verified Successfully",
        "stderr must be empty",
        "separate invocations",
        "present and hash-verified before any candidate release is trusted",
        "never reach the target host",
        "never reach the target host, release bundle, backup, manifest, log, process environment, or OAS state",
        "four signatures total",
        "retired or revoked key cannot authorize rollback",
        "Verification fails closed",
    )
    argv_blocks = [
        block.splitlines()
        for block in _code_blocks(section)
        if block.startswith("/usr/bin/openssl\n")
    ]
    assert argv_blocks == [[
        "/usr/bin/openssl",
        "pkeyutl",
        "-verify",
        "-rawin",
        "-in",
        "/var/lib/aether/install/<tx>/verify/<role>-signed-bytes.bin",
        "-sigfile",
        "/var/lib/aether/install/<tx>/verify/<role>-signature.raw",
        "-inkey",
        "/var/lib/aether/install/<tx>/verify/<role>-key.spki.der",
        "-pubin",
        "-keyform",
        "DER",
    ]]
    anchor_definition = next(
        block for block in _code_blocks(section) if block.startswith("ANCHOR_DOMAIN =")
    )
    assert "anchor_fingerprint" not in next(
        line for line in anchor_definition.splitlines()
        if line.startswith("ANCHOR_FINGERPRINT =")
    )


def test_python_import_environment_and_service_home_are_coherent():
    text = _text()
    section = _section(text, "## 6. Python Runtime, Import Roots, and Environment", "## 7. Principals, Filesystem, and Canonical State")
    env_block = next(block for block in _code_blocks(section) if "PROTOCOL_ENVIRONMENT:" in block)
    allowed = {
        line.split("=", 1)[0].strip()
        for line in env_block.splitlines()
        if line.strip() and not line.endswith(":")
    }
    assert allowed == {
        "LISTEN_PID",
        "LISTEN_FDS",
        "LISTEN_FDNAMES",
        "NOTIFY_SOCKET",
        "LANG",
        "LC_ALL",
        "TZ",
        "HOME",
    }
    unit = _unit_block(text)
    unit_environment = {
        line.split("=", 1)[1].split("=", 1)[0]
        for line in unit.splitlines()
        if line.startswith("Environment=")
    }
    assert unit_environment == {"LANG", "LC_ALL", "TZ", "HOME"}
    assert not any(line.startswith("Environment=PYTHON") for line in unit.splitlines())
    _require(
        _normalized(section),
        "-I -B -S",
        "/opt/aether/current/runtime/lib/python3.11/site-packages",
        "Current working directory",
        "No",
        "User site",
        "System site packages",
        "Development checkout",
        "Python hash randomization is not required to be deterministic",
        "`-B` is the sole bytecode-disable mechanism",
        "`-I` ignores Python environment variables",
        "/var/empty",
        "INVOCATION_ID",
        "JOURNAL_STREAM",
        "PATH",
        "USER",
        "LOGNAME",
        "SHELL",
        "SYSTEMD_EXEC_PID",
        "ambient non-authority metadata",
        "are not a startup failure merely because systemd supplied them",
        "clears all other environment entries",
    )
    command = next(line for line in unit.splitlines() if line.startswith("ExecStart="))
    assert " -I -B -S -c " in command
    assert 'sys.path.insert(0,"/opt/aether/current/runtime/lib/python3.11/site-packages")' in command
    assert "from aether.oas.host_entrypoint import main" in command
    assert "PYTHONHASHSEED=0" not in unit


def test_service_unit_sections_vocabulary_placeholders_and_enablement_are_exact():
    text = _text()
    sections = _parse_service_unit(text)
    unit_keys = {key for key, _value in sections["Unit"]}
    service_keys = {key for key, _value in sections["Service"]}
    assert {
        "Description",
        "Requires",
        "After",
        "ConditionPathExists",
        "AssertPathExists",
        "StartLimitIntervalSec",
        "StartLimitBurst",
        "StartLimitAction",
    } <= unit_keys
    assert {
        "Sockets",
        "User",
        "Group",
        "SupplementaryGroups",
        "ExecStart",
        "WorkingDirectory",
        "Environment",
        "UMask",
        "Type",
        "NotifyAccess",
        "Restart",
        "RestartSec",
        "TimeoutStartSec",
        "TimeoutStopSec",
        "FileDescriptorStoreMax",
        "LimitNOFILE",
        "TasksMax",
        "MemoryMax",
        "CPUQuota",
    } <= service_keys
    assert "Sockets" not in unit_keys
    assert not {"StartLimitIntervalSec", "StartLimitBurst", "StartLimitAction"} & service_keys
    assert sections["Install"] == []
    assert "not independently enabled" in _normalized(text)
    placeholders = set(re.findall(r"<[^>]+>", _unit_block(text)))
    assert placeholders == {"<generation>"}
    assert "replaced by the unit bundle's fixed 64-hex generation at Build time" in text


def test_unit_generation_protocol_is_non_atomic_and_blocks_mixed_activation():
    text = _text()
    section = _section(text, "## 9. Unit-Generation Transaction and Power Loss", "## 10. Executable Systemd Resource and Hardening Contract")
    quiesce = _table(section, ["Quiesce step", "Root action", "Required proof or failure result"])
    assert [row["Quiesce step"] for row in quiesce] == [str(number) for number in range(1, 8)]
    assert "Stop new admission" in quiesce[0]["Root action"]
    assert "Stop all three socket units" in quiesce[1]["Root action"]
    assert "Stop `aether-oas.service`" in quiesce[2]["Root action"]
    assert "no OAS process, accepted connection" in quiesce[4]["Root action"]
    assert "abort" in quiesce[5]["Required proof or failure result"]
    assert "old generation still authoritative" in quiesce[4]["Required proof or failure result"]
    _require(
        _normalized(section).lower(),
        "stop new admission",
        "all three socket units",
        "bounded m120a shutdown",
        "no oas process, accepted connection, socket unit, listener, activation job, or outstanding worker",
        "systemd unit state and the service cgroup",
        "before any gate invalidation",
        "does not stop an already-running socket or service",
        "absent generation gate",
    )
    steps = _table(section, ["Step", "Root action", "Required durable condition"])
    assert [row["Step"] for row in steps] == [str(number) for number in range(1, 13)]
    assert "Invalidate the old live generation gate" in steps[5]["Root action"]
    assert "Replace each live unit independently" in steps[6]["Root action"]
    assert "Atomically install candidate" in steps[9]["Root action"]
    assert "Verify `systemctl cat`, effective properties" in steps[8]["Root action"]
    boot = _table(section, ["Boot condition", "Unit result", "Recovery result"])
    assert len(boot) == 6
    assert any("mixed" in row["Boot condition"].lower() and "no socket creation" in row["Recovery result"].lower() for row in boot)
    assert any("missing" in row["Boot condition"].lower() and "condition-failed" in row["Unit result"] for row in boot)
    _require(
        _normalized(section),
        "g-<64 lowercase hexadecimal unit-bundle digest>",
        "Every complete four-unit bundle has one generation ID",
        "All four units in that generation contain an exact generation-specific `ConditionPathExists`",
        "No operation claims atomicity across the four files",
        "Code-only activation leaves the unit generation unchanged",
    )
    assert "atomically replaces the unit files" not in text


def test_systemd_socket_order_and_dependency_contract_are_explicit():
    text = _text()
    section = _section(text, "## 8. Systemd Socket Set and Descriptor Order", "## 9. Unit-Generation Transaction and Power Loss")
    ordered = _table(section, ["Order", "FD", "Socket unit", "`FileDescriptorName`", "Path", "Expected peer"])
    assert [(row["Order"], row["FD"], row["`FileDescriptorName`"]) for row in ordered] == [
        ("1", "3", "`runtime`"),
        ("2", "4", "`bootstrap`"),
        ("3", "5", "`broker`"),
    ]
    assert [row["Socket unit"] for row in ordered] == [
        "`aether-oas-runtime.socket`",
        "`aether-oas-bootstrap.socket`",
        "`aether-oas-broker.socket`",
    ]
    unit = _unit_block(text)
    assert unit.split("Sockets=", 1)[1].splitlines()[0] == (
        "aether-oas-runtime.socket aether-oas-bootstrap.socket aether-oas-broker.socket"
    )
    requires = next(line for line in unit.splitlines() if line.startswith("Requires="))
    assert requires.split("=", 1)[1].split() == [
        "aether-oas-runtime.socket",
        "aether-oas-bootstrap.socket",
        "aether-oas-broker.socket",
    ]
    after = next(line for line in unit.splitlines() if line.startswith("After="))
    assert after.split("=", 1)[1].split()[-3:] == [
        "aether-oas-runtime.socket",
        "aether-oas-bootstrap.socket",
        "aether-oas-broker.socket",
    ]
    assert "Requires=aether-oas.service" not in {
        line.strip() for line in section.splitlines()
    }
    _require(
        _normalized(section),
        "Starting one socket manually is not a partial-service path",
        "Direct `systemctl start aether-oas.service` likewise requires the complete ordered set",
        "Queued connections are intentionally rejected during that boundary",
        "explicit order",
        "LISTEN_FDNAMES=runtime:bootstrap:broker",
        "LISTEN_FDS=3",
    )


def test_resource_calculation_restart_policy_and_directives_are_executable():
    text = _text()
    resource_section = _section(text, "## 10. Executable Systemd Resource and Hardening Contract", "## 11. Root Installation, Migration, Rollback, and Recovery")
    resources = _table(resource_section, ["Resource", "Count"])
    counts = {row["Resource"]: int(row["Count"]) for row in resources}
    assert counts["Activated listening sockets"] == 3
    assert counts["Accepted client connections, 32 active + 64 queued"] == 96
    assert counts["SQLite-related descriptors, 32 connections x database/WAL/SHM"] == 96
    assert counts["Explicit reserve"] == 64
    assert counts["Conservative total"] == 284
    unit = _unit_block(text)
    assert "LimitNOFILE=512" in unit
    assert "FileDescriptorStoreMax=0" in unit
    assert 512 - counts["Conservative total"] == 228
    for expected in (
        "Restart=on-failure",
        "RestartSec=2s",
        "StartLimitIntervalSec=60s",
        "StartLimitBurst=5",
        "StartLimitAction=none",
    ):
        assert expected in unit
    directives = _table(resource_section, ["Directive", "systemd 252 meaning and access consequence"])
    names = {row["Directive"] for row in directives}
    assert {
        "`RestrictNamespaces=yes`",
        "`ConditionPathExists=` and `AssertPathExists=`",
        "`LimitCORE=0`",
        "`TasksMax=128`",
        "`MemoryMax=512M`, `CPUQuota=100%`",
        "`Type=notify`, `NotifyAccess=main`",
    } <= names
    _require(
        _normalized(resource_section),
        "Boolean yes denies creation and entry of all process namespaces",
        "No automatic fallback is permitted",
        "Unsupported mandatory hardening fails closed",
        "`/var/log/aether` path",
        "Systemd may terminate the process at its stop deadline",
        "never as successful shutdown",
    )
    assert "LimitNOFILE=128" not in text


def test_build_inventory_and_stage_boundaries_are_complete():
    section = _section(_text(), "## 14. Future Repository Build Boundary", "## 15. Exclusions, Status, and Stop Boundary")
    rows = _table(section, ["Category", "Proposed path", "Required artifact/test"])
    categories = {row["Category"] for row in rows}
    assert categories == {
        "Production OAS entrypoint",
        "Native systemd notification",
        "Manifest schema",
        "Manifest generator",
        "Release verifier",
        "Dependency lock/wheelhouse",
        "Four units",
        "Fixed installer",
        "Lifecycle/rollback tool",
        "Offline unit verifier",
        "Evidence collector",
        "Artifact-specific tests",
    }
    stages = _table(section, ["Stage", "Scope", "Authorization boundary"])
    assert [row["Stage"] for row in stages] == [
        "Build stage",
        "Isolated proof stage",
        "Target deployment stage",
        "Deployment review stage",
    ]
    assert "Separate PM-approved repository Build; no host mutation" in stages[0]["Authorization boundary"]
    assert "Not authorized by M121A" in stages[2]["Authorization boundary"]
    assert "Required before `DEPLOYMENT_VERIFIED`" in stages[3]["Authorization boundary"]
    _require(
        section,
        "No automatic sequence combines repository Build with live root deployment",
        "aether/oas/host_entrypoint.py",
        "aether/oas/systemd_notify.py",
        "deployment/requirements.lock.json",
        "deployment/systemd/aether-oas.service",
        "aether/deployment/installer.py",
        "aether/deployment/lifecycle.py",
        "aether/deployment/unit_verifier.py",
        "aether/deployment/evidence_collector.py",
    )


def test_status_exclusions_and_unimplemented_boundary_are_exact():
    text = _text()
    status = _status_block(text)
    assert status == {
        "M121A_SECOND_CORRECTIVE_PASS_COMPLETE": "YES",
        "M121A_CORRECTIVE_PASS_COMPLETE": "YES",
        "M121A_AUTHORIZED": "YES",
        "M121A_STARTED": "YES",
        "M121A_FINALIZED": "NO",
        "DECISION_STATUS": "CURRENT",
        "DESIGN_STATUS": "DESIGN_PROVEN",
        "IMPLEMENTATION_STATUS": "NOT_IMPLEMENTED",
        "VERIFICATION_STATUS": "TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED": "NO",
        "SELECTED_EXIT": "EXIT_A",
        "BUILD_AUTHORIZED": "NO",
        "HOST_MUTATION_PERFORMED": "NO",
        "PROGRESS_UPDATED": "NO",
        "SECURITY_ARCHITECTURE_UPDATED": "NO",
        "COMMIT_CREATED": "NO",
        "TAG_CREATED": "NO",
        "PUSH_PERFORMED": "NO",
        "SUCCESSOR_AUTHORIZED": "NO",
        "SUCCESSOR_NUMBER_ASSIGNED": "NO",
        "READY_FOR_PM_REVIEW": "YES",
    }
    exclusions = _normalized(_tail(text, "## 15. Exclusions, Status, and Stop Boundary"))
    _require(
        exclusions,
        "update `PROGRESS.md`",
        "update `SECURITY_ARCHITECTURE.md`",
        "modify production code or existing tests",
        "create units, an installer, an entrypoint, a release bundle, a manifest, a verifier, or a rollback tool",
        "install dependencies or packages",
        "create or modify users, groups, permissions, mounts, services, sockets, or host configuration",
        "claim a read-only mount, live principal, live unit, readiness, or deployment verification",
        "commit, tag, push, or modify any Git reference",
        "authorize or number a successor milestone",
        "another PM hard-gate review",
    )
    # M122A is the separately authorized successor Build.  The predecessor
    # document remains unchanged; this lock only stops asserting that its
    # successor's artifact paths must be absent.
    assert text.count("M121A_FINALIZED: NO") == 1
    assert "/opt/aether/active-release" not in text
    assert "InaccessiblePaths=/home /root /var/log/aether" not in text
