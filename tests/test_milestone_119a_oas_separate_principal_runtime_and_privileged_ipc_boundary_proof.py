"""Static structural proof lock for the corrected M119A host contract."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / (
    "docs/architecture/"
    "MILESTONE_119A_OAS_SEPARATE_PRINCIPAL_RUNTIME_AND_PRIVILEGED_IPC_BOUNDARY_PROOF.md"
)


def _text() -> str:
    return PROOF.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def _tail(text: str, heading: str) -> str:
    return text[text.index(heading):]


def _markers(text: str, *values: str) -> None:
    for value in values:
        assert value in text, value


def _data_rows(section: str) -> list[str]:
    rows = [
        line
        for line in section.splitlines()
        if line.startswith("|")
        and set(line.replace("|", "").replace("-", "").replace(" ", ""))
    ]
    return rows[1:]


def test_record_has_complete_unique_structure():
    text = _text()
    assert PROOF.is_file()
    required = [
        "## 1. Authority, Scope, and Corrected Decision",
        "## 2. Read-Only Discovery and Current Truth",
        "### 2.1 Host facts",
        "### 2.2 Current runtime, data, and startup",
        "## 3. Corrected Principal Model",
        "## 4. Candidate Models and Launcher Selection",
        "## 5. Human Presence, Fresh Authentication, and Intent",
        "## 6. Exact Authorization Context Contract",
        "## 7. Filesystem Contract",
        "## 8. Systemd Socket-Activation and Responsibility Contract",
        "### 8.1 Socket units",
        "### 8.2 OAS service unit target",
        "### 8.3 Owner broker service unit target",
        "## 9. OAS IPC Protocol and Allowed Operations",
        "## 10. Startup, Crash, Shutdown, Migration, and Backup",
        "## 11. Threat Model and Corrected Runtime Analysis",
        "## 12. Test and Deployment-Verification Boundary",
        "## 13. Explicit Exclusions and M119A Status",
    ]
    headings = re.findall(r"^#{2,3} .+$", text, flags=re.MULTILINE)
    for heading in required:
        assert headings.count(heading) == 1, heading
    assert len(headings) == len(required)
    assert len(text.splitlines()) >= 500
    assert "## 14." not in text


def test_authority_and_core_aether_boundaries_are_structured():
    section = _normalized(
        _section(
            _text(),
            "## 1. Authority, Scope, and Corrected Decision",
            "## 2. Read-Only Discovery and Current Truth",
        )
    )
    _markers(
        section,
        "CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION",
        "Milestone records are design evidence and traceability records, not another authority layer.",
        "Aether remains one persistent digital mind.",
        "AetherOS is its operating environment and body.",
        "OAS is a bounded authority service, not a second mind, agent, or cognitive runtime.",
        "Authentication is not intent interpretation.",
        "Goal acceptance is not Action authorization.",
        "Action success is not completion.",
        "Completion requires Observation and Verification.",
        "M118A proves only a bounded durable SQLite security kernel.",
        "The design is internally executable on a host",
    )


def test_discovery_records_host_and_current_runtime_without_claiming_deployment():
    text = _text()
    host = _normalized(_section(text, "### 2.1 Host facts", "### 2.2 Current runtime, data, and startup"))
    runtime = _normalized(_section(text, "### 2.2 Current runtime, data, and startup", "## 3. Corrected Principal Model"))
    _markers(
        host,
        "Debian GNU/Linux 12 (bookworm), x86_64",
        "systemd 252, PID 1, system running",
        "`aether`, uid/gid 1000",
        "`sudo`",
        "No `oas` user or group exists",
        "ext4",
        "`AF_UNIX`, `SO_PEERCRED`, `SCM_CREDENTIALS`, `SCM_RIGHTS`",
        "Docker and Podman not found",
        "`getfacl`, `aa-status`, and `getenforce` not available",
        "current development account is login-capable and belongs to sudo",
    )
    _markers(
        runtime,
        "no OAS import, startup/lifespan hook, authentication middleware, TLS listener, or service launcher",
        "one process-global `AetherRuntime`",
        "`/chat` explicitly disables tool execution",
        "static code/dependency boundary",
        "caller-supplied SQLite path",
        "No Aether or OAS service/socket unit",
        "deployment artifact exists in the repository",
    )


def test_principal_table_proves_human_runtime_uid_separation():
    section = _section(_text(), "## 3. Corrected Principal Model", "## 4. Candidate Models and Launcher Selection")
    rows = _data_rows(section)
    assert len(rows) == 5
    _markers(
        _normalized(section),
        "`aether-owner`, dedicated local-login uid/gid",
        "`aether-runtime`, dedicated non-login service uid/gid",
        "`aether-oas`, dedicated non-login service uid/gid",
        "`aether-bootstrap`, dedicated non-login helper uid/gid",
        "`root` through explicitly bounded host procedures",
        "never share a uid",
        "not login-capable",
        "current `aether` account's sudo membership and session bus are not inherited",
    )


def test_candidate_comparison_and_exact_launcher_chain_are_complete():
    section = _section(_text(), "## 4. Candidate Models and Launcher Selection", "## 5. Human Presence, Fresh Authentication, and Intent")
    rows = _data_rows(section)
    assert len(rows) == 5
    for candidate in ("A.", "B.", "C.", "D.", "E."):
        assert any(candidate in row for row in rows), candidate
    _markers(
        _normalized(section),
        "Root-owned AF_UNIX privileged broker",
        "Polkit/PAM-mediated privileged launcher",
        "Tightly scoped sudo/PAM command",
        "Selected exact mechanism: one root broker",
        "No truthful model",
        "HUMAN OWNER aether-owner",
        "owner-broker.sock via SO_PEERCRED",
        "root owner broker: logind active-local-session gate",
        "one-shot PAM authentication and TTY confirmation",
        "broker registers one-use context on OAS broker.sock",
        "root broker launches fixed /usr/libexec/aether-oas-bootstrap",
        "helper presents context on OAS bootstrap.sock via SO_PEERCRED",
        "M118A-bound OAS transaction and audit",
        "not a standalone executable",
    )


def test_human_ceremony_closes_presence_and_fresh_intent_gap():
    section = _normalized(_section(_text(), "## 5. Human Presence, Fresh Authentication, and Intent", "## 6. Exact Authorization Context Contract"))
    _markers(
        section,
        "`aether-owner`",
        "peer.uid == uid(aether-owner)",
        "logind.User == aether-owner",
        "logind.Active == true",
        "logind.Remote == false",
        "logind.Type == tty",
        "logind.Class == user",
        "pam_start",
        "aether-oas-owner-bootstrap",
        "fresh interactive authentication",
        "SSH, remote terminals, forwarded agents, API calls",
        "expires after 60 seconds",
        "fresh 128-bit confirmation nonce",
        "BEGIN_LOCAL_BOOTSTRAP_WINDOW",
        "exact Aether Instance ID",
        "current trust generation",
        "human must type the displayed confirmation",
        "Aether Instance ID and expected generation therefore come from OAS",
        "`aether-runtime` cannot invoke or satisfy",
    )


def test_authorization_context_table_covers_lifecycle_and_pid_reuse():
    section = _section(_text(), "## 6. Exact Authorization Context Contract", "## 7. Filesystem Contract")
    rows = _data_rows(section)
    assert len(rows) == 13
    _markers(
        _normalized(section),
        "Creator",
        "256-bit random opaque `context_id`",
        "broker-held and OAS-registered",
        "Protocol version, context ID, request ID, operation",
        "Aether Instance ID",
        "expected trust generation",
        "Maximum 60 seconds by monotonic clock",
        "private `AF_UNIX` `SOCK_SEQPACKET` socketpair",
        "inherited descriptor 3",
        "OAS validation",
        "PID is audit-only and never an authority binding",
        "one-use",
        "changed content or a second use is a conflict",
        "OAS revokes all volatile contexts on service restart",
        "OAS owns the durable audit event",
        "not client-supplied `SCM_RIGHTS`",
    )


def test_filesystem_contract_covers_database_side_files_and_no_runtime_write():
    section = _section(_text(), "## 7. Filesystem Contract", "## 8. Systemd Socket-Activation and Responsibility Contract")
    rows = _data_rows(section)
    assert len(rows) == 9
    _markers(
        _normalized(section),
        "/var/lib/aether/oas",
        "/run/aether/oas",
        "root:root",
        "aether-oas:aether-oas",
        "mode `0700`",
        "`0600`",
        "SQLite `-wal` and `-shm`",
        "Backup staging",
        "UMask=0077",
        "fails closed",
        "ordinary runtime service has no write permission",
    )


def test_socket_activation_resolves_creation_and_ownership_contradiction():
    section = _section(_text(), "## 8. Systemd Socket-Activation and Responsibility Contract", "## 9. OAS IPC Protocol and Allowed Operations")
    socket_rows = _data_rows(_section(section, "### 8.1 Socket units", "### 8.2 OAS service unit target"))
    assert len(socket_rows) == 4
    _markers(
        _normalized(section),
        "Model S1, systemd socket activation, is selected.",
        "OAS never binds, chowns, renames, or removes endpoint files.",
        "ListenSequentialPacket=",
        "Accept=no",
        "DirectoryMode=0755",
        "RemoveOnStop=yes",
        "aether-oas-runtime.socket",
        "aether-oas-bootstrap.socket",
        "aether-oas-broker.socket",
        "aether-oas-owner-broker.socket",
        "exactly three descriptors named runtime, bootstrap, and broker",
        "descriptor count, `SOCK_SEQPACKET` type, listening state",
        "device/inode match",
        "No client can create, rename, replace, or remove",
    )


def test_systemd_service_values_and_responsibility_split_are_exact():
    section = _normalized(_section(_text(), "### 8.2 OAS service unit target", "## 9. OAS IPC Protocol and Allowed Operations"))
    broker = _normalized(_section(_text(), "### 8.3 Owner broker service unit target", "## 9. OAS IPC Protocol and Allowed Operations"))
    _markers(
        section,
        "User=aether-oas",
        "Group=aether-oas",
        "SupplementaryGroups=",
        "RuntimeDirectory= (not used",
        "StateDirectory= (not used",
        "NoNewPrivileges=yes",
        "PrivateTmp=yes",
        "PrivateDevices=yes",
        "ProtectSystem=strict",
        "ProtectHome=yes",
        "ReadWritePaths=/var/lib/aether/oas",
        "RestrictAddressFamilies=AF_UNIX",
        "RestrictSUIDSGID=yes",
        "CapabilityBoundingSet=",
        "AmbientCapabilities=",
        "LimitCORE=0",
        "Restart=on-failure",
        "RestartSec=2s",
        "TimeoutStartSec=30s",
        "TimeoutStopSec=10s",
        "Type=notify",
        "OAS does not need write access to `/run/aether/oas`",
    )
    _markers(
        broker,
        "User=root",
        "Group=root",
        "NoNewPrivileges=no",
        "PrivateDevices=no",
        "CapabilityBoundingSet=CAP_SETUID CAP_SETGID",
        "verified local controlling TTY",
        "no OAS state path",
        "drops all supplementary groups",
        "passes only descriptor 3",
        "execs the root-owned fixed helper",
    )


def test_ipc_operations_and_bounds_cannot_form_generic_mutation_client():
    section = _normalized(_section(_text(), "## 9. OAS IPC Protocol and Allowed Operations", "## 10. Startup, Crash, Shutdown, Migration, and Backup"))
    _markers(
        section,
        "AF_UNIX` `SOCK_SEQPACKET",
        "SO_PEERCRED",
        "exact `aether-runtime`",
        "exact `aether-bootstrap`",
        "PING",
        "GET_BOUNDED_RUNTIME_STATUS",
        "BEGIN_LOCAL_BOOTSTRAP_WINDOW",
        "CANCEL_LOCAL_BOOTSTRAP_WINDOW",
        "ISSUE_LOCAL_BOOTSTRAP_CHALLENGE",
        "REGISTER_LOCAL_BOOTSTRAP_AUTHORIZATION",
        "REVOKE_LOCAL_BOOTSTRAP_AUTHORIZATION",
        "No endpoint accepts SQL",
        "generic mutation requests",
        "4096 bytes",
        "16384 bytes",
        "one committed result",
    )


def test_lifecycle_migration_backup_and_logging_contracts_are_explicit():
    section = _normalized(_section(_text(), "## 10. Startup, Crash, Shutdown, Migration, and Backup", "## 11. Threat Model and Corrected Runtime Analysis"))
    _markers(
        section,
        "Startup ordering is",
        "systemd socket units create",
        "OAS validates descriptor count",
        "startup migration as `aether-oas`",
        "publishes readiness",
        "stops service readiness",
        "SQLite atomicity rolls back",
        "same request identity",
        "all volatile authorization contexts are revoked",
        "Only root may install or upgrade",
        "allowlisted OAS procedure",
        "schema/integrity/identity/generation",
        "Backups are root-owned mode `0700`",
        "Audit records remain OAS-owned",
        "Service core dumps are disabled",
    )


def test_threat_table_covers_compromised_runtime_and_root_boundary():
    section = _section(_text(), "## 11. Threat Model and Corrected Runtime Analysis", "## 12. Test and Deployment-Verification Boundary")
    rows = _data_rows(section)
    assert len(rows) == 16
    threats = (
        "Compromised `aether-runtime` process",
        "Runtime becomes human Owner",
        "Runtime invokes privileged launcher",
        "Runtime satisfies fresh human authentication",
        "Runtime joins Owner/bootstrap groups",
        "Runtime executes helper as target uid",
        "Runtime connects to bootstrap endpoint",
        "Runtime steals/replays context",
        "Runtime writes OAS code or units",
        "Runtime writes state/WAL/SHM",
        "Runtime writes socket directory",
        "Runtime accesses backups/logs",
        "Runtime uses status as mutation oracle",
        "Socket activation widens authority",
        "Service restart widens authority",
        "Root/administrator compromise",
    )
    for threat in threats:
        assert any(threat in row for row in rows), threat
    _markers(
        _normalized(section),
        "Different uid",
        "Cannot access Owner TTY/session bus",
        "No readable context file/env/argv",
        "Root remains the host trust base.",
        "No protection against root compromise is claimed.",
    )


def test_status_exclusions_and_exit_preserve_finalized_nonbuild_state():
    text = _text()
    exclusions = _normalized(_section(text, "## 13. Explicit Exclusions and M119A Status", "The exact M119A lifecycle/status block is:"))
    status = _tail(text, "The exact M119A lifecycle/status block is:")
    _markers(
        exclusions,
        "production OAS code or service behavior",
        "users, groups, services, sockets, credentials, PAM/polkit rules, sudoers, or deployment files",
        "canonical Security Architecture or PROGRESS.md status",
        "WebAuthn request semantics",
        "Goal operations",
        "AuthenticatedSourceEvent issuance",
        "Generic Act",
        "a Build milestone or a successor milestone number",
    )
    _markers(
        status,
        "M119A_AUTHORIZED: YES",
        "M119A_STARTED: YES",
        "M119A_FINALIZED: YES",
        "DECISION_STATUS: CURRENT",
        "DESIGN_STATUS: DESIGN_PROVEN",
        "IMPLEMENTATION_STATUS: NOT_IMPLEMENTED",
        "VERIFICATION_STATUS: TEST_VERIFIED",
        "DEPLOYMENT_VERIFIED: NO",
        "BUILD_JUSTIFIED_FOR_PM_REVIEW: YES",
        "BUILD_AUTHORIZED: NO",
        "PROGRESS_UPDATED: YES",
        "SECURITY_ARCHITECTURE_UPDATED: YES",
        "COMMIT_CREATED: YES",
        "TAG_CREATED: YES",
        "PUSH_PERFORMED: YES",
        "SUCCESSOR_NUMBER_ASSIGNED: NO",
        "PM_ACCEPTED: YES",
        "Selected exit: `EXIT_A`.",
        "It is not Build authorization.",
    )
    assert "BUILD_AUTHORIZED: YES" not in status


def test_static_proof_is_read_only_and_does_not_import_application_code():
    source = Path(__file__).read_text(encoding="utf-8")
    assert not re.search(r"^(?:from|import)\s+aether\b", source, flags=re.MULTILINE)
    assert not re.search(r"^(?:from|import)\s+(?:subprocess|socket|os)\b", source, flags=re.MULTILINE)
    assert not re.search(r"\bos\.system\s*\(", source)
    assert not re.search(r"\bsocket\.socket\s*\(", source)
