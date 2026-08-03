from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RECORD = ROOT / "docs/architecture/MILESTONE_86_ARCHITECTURE_EVOLUTION_DECISION.md"
ARCHITECTURE = ROOT / "docs/ARCHITECTURE.md"
README = ROOT / "README.md"
CONSTITUTION = ROOT / "docs/CONSTITUTION.md"
M85_RECORD = ROOT / "docs/architecture/MILESTONE_85_OBSERVE_VERIFY_LIFECYCLE_BOUNDARY_RECORD.md"
API_SERVER = ROOT / "aether/interface/api_server.py"

TITLE = "# Milestone 86 Architecture Evolution Decision"

SECTIONS = (
    "## 1. Status and Scope",
    "## 2. Purpose",
    "## 3. Authoritative Existing Baseline",
    "## 4. Authorization and Rejected Plan",
    "## 5. Corrected Architecture Model",
    "## 6. Identity Anchor and Identity Organ",
    "## 7. Core Governance",
    "## 8. Cognitive Signal Arbitration — Hard Constraints and Soft Signals",
    "## 9. Thinking and Governance Responsibility Split",
    "## 10. Authoritative Shared Cognitive Context",
    "## 11. Shared Context Ownership Map",
    "## 12. State and Memory Separation",
    "## 13. Temporal Context — Four Time Semantics and Five Scopes",
    "## 14. Controlled Background Continuity",
    "## 15. Resource Observation and Resource Governance",
    "## 16. Optional Economic Capability",
    "## 17. Architecture Invariant Set and Regression Locks",
    "## 18. Placement Map",
    "## 19. Relationship to Existing Records",
    "## 20. Future Capability Gates and Milestone 86 Closure Rule",
)

INVARIANTS = (
    "1. One Persistent Identity",
    "2. Nine Cognitive Organs Remain",
    "3. Governance Is Cross-Cutting",
    "4. Coordination Is Cross-Cutting",
    "5. One ASC Architecture Framework",
    "6. One Authoritative Context Per Active Task",
    "7. One Current Task Context Per Reasoning Turn",
    "8. No Silent Cross-Task Context Merging",
    "9. Context Is Not Memory",
    "10. Every Authoritative Category Has an Owner",
    "11. Read Access Does Not Imply Write Authority",
    "12. Hard Constraints Before Optimization",
    "13. Time Provides Context, Not Authority",
    "14. Resource Observation Reports, Governance Decides",
    "15. Resource Facts Are Time-Bounded",
    "16. Background Continuity Does Not Create Authority",
    "17. Budget Cannot Override Safety",
    "18. Current State and Historical Trace Are Separate",
    "19. Optional Extensions Cannot Redefine the Core",
    "20. Thinking Proposes, Governance Authorizes",
    "21. Canonical Execution Loop Remains Unchanged",
    "22. Milestone 85 Observation/Verification Boundary Remains in Force",
    "23. Milestone 86 Adds No Runtime Capability",
)

SECTION_18_SUBSECTIONS = (
    "### 18.1 Evolution Scope and One-Mind Model",
    "### 18.2 Identity and Constitutional Foundation",
    "### 18.3 Cross-Cutting Governance and Coordination",
    "### 18.4 Core Governance",
    "### 18.5 Execution and Context Relationship",
    "### 18.6 Authoritative Shared Cognitive Context",
    "### 18.7 Context Ownership and State Separation",
    "### 18.8 Cognitive Signal Arbitration and Policy Boundary",
    "### 18.9 Resource Observation and Resource Governance",
    "### 18.10 Controlled Background Continuity",
    "### 18.11 Time Reasoning and AetherOS Timing Boundary",
    "### 18.12 Optional Economic Capability",
    "### 18.13 Architecture Invariants and Existing-Record Relationship",
    "### 18.14 Future Capability Gates and Milestone 86 Closure Rule",
)

SUPERSESSION_CLAUSE = (
    "This revision is the explicitly authorized architecture evolution for Milestone 86. "
    "It incorporates the Milestone 85 Observation Classification / Verification Aggregation / "
    "Lifecycle Decision Boundary Record by reference and does not alter it; that record remains "
    "fully in force. The governance, coordination, and infrastructure sections added by this "
    "revision extend the architecture without reopening the observation/verification boundary."
)

README_ADDITION = (
    "Aether coordinates its work through an authoritative shared cognitive-context framework. "
    "Each active task has one authoritative context, and governance and coordination are "
    "internal cross-cutting layers of one persistent mind, not separate agents."
)

CANONICAL_LOOP = (
    "Receive Goal → Understand → Think → Plan → Act → Observe → Verify → Critic → Repair → Learn → Report"
)

FORBIDDEN_DOC_TOKENS = (
    "Test" + "Client",
    "Fast" + "API",
    "from aether" + ".interface",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def test_checks_1_to_3_record_path_title_and_20_sections():
    assert RECORD.exists()
    text = _read(RECORD)
    assert TITLE in text
    for section in SECTIONS:
        assert section in text


def test_check_4_record_is_documentation_only_no_runtime_capability():
    text = _normalized(RECORD)
    for marker in (
        "introduces no runtime capability",
        "no queue, no store, no persistence directory, no schema, no router",
        "no scheduler, and no agent",
        "no aether/* source changes",
        "contracts in documentation only",
    ):
        assert marker in text


def test_check_5_one_persistent_identity():
    text = _normalized(RECORD)
    for marker in (
        "Aether is one persistent mind",
        "one continuous identity",
        "one identity, one mind, one agent",
        "no second mind or agent",
        "foundational continuity and constitutional reference of the same single Aether identity",
        "not a second Identity component, not a second cognitive organ, and not a second authority source",
        "The anchor is a reference, not a duplicate",
        "loads, represents, protects, and verifies that same continuous identity",
        "The Identity organ is not itself described as a separate foundational identity or parallel identity state",
    ):
        assert marker in text


def test_check_6_nine_cognitive_organs_remain():
    text = _normalized(RECORD)
    for organ in (
        "Identity",
        "Time",
        "Memory",
        "Perception",
        "Thinking",
        "Verification",
        "Action",
        "Learning",
        "Interface",
    ):
        assert organ in text
    assert "Nine Cognitive Organs Remain" in text


def test_check_7_8_governance_and_coordination_are_cross_cutting_not_agents():
    text = _normalized(RECORD)
    for marker in (
        "Core Governance is an internal cross-cutting layer",
        "never a separate agent",
        "Core Coordination is an internal cross-cutting layer of the single mind",
        "spans every Execution Loop stage",
    ):
        assert marker in text


def test_check_9_signal_arbitration_belongs_to_governance():
    text = _normalized(RECORD)
    assert "Cognitive Signal Arbitration belongs to Core Governance" in text


def test_check_10_11_temporal_reasoning_owned_by_time_aetheros_mechanisms_only():
    text = _normalized(RECORD)
    for marker in (
        "Temporal Context and Multi-timescale Reasoning belong to the Time cognitive organ",
        "AetherOS Infrastructure supplies only timing mechanisms and raw clock facts",
        "Temporal reasoning is cognition, not infrastructure",
    ):
        assert marker in text


def test_check_12_asc_exact_name_framework_not_global_object():
    text = _normalized(RECORD)
    for marker in (
        "Authoritative Shared Cognitive Context (ASC)",
        "architecture framework, not one global mutable task object",
        "The ASC framework is owned by Core Coordination",
        "One ASC architecture framework exists",
        "Every active task has exactly one authoritative task context",
        "One reasoning turn has exactly one current task context",
    ):
        assert marker in text


def test_check_13_asc_non_goals():
    text = _normalized(RECORD)
    for marker in (
        "the ASC is not a database",
        "not a memory tier",
        "not a scheduler",
        "not a queue",
        "not a new cognitive organ",
        "not an authorization source",
    ):
        assert marker in text


def test_check_14_asc_four_categories():
    text = _normalized(RECORD)
    for marker in (
        "Goal and Task Context",
        "Authority and Governance Context",
        "Operational Context",
        "Cognitive References",
    ):
        assert marker in text


def test_check_15_16_current_context_and_no_silent_merging():
    text = _normalized(RECORD)
    for marker in (
        "One framework, one authoritative context per active task",
        "One reasoning turn, one current task context",
        "No silent cross-task context merging",
        "Waiting, paused, or background tasks may retain separate task contexts",
        "Switching the current task context is an explicit Core Coordination operation",
    ):
        assert marker in text


def test_check_17_18_ownership_one_owner_and_read_vs_write():
    text = _normalized(RECORD)
    for marker in (
        "Every authoritative category has exactly one owner",
        "Read access does not imply write authority",
        "A contributor may propose an update without becoming the owner",
        "Current Goal: Human Authority",
        "Active Task: Core Coordination",
        "Permission Scope: Human Authority and Core Governance",
        "Risk Classification: Verification supplies evidence",
        "Resource Budget: Resource Governance",
        "Completion Criteria: the Plan stage and planning contract define",
        "Approval State: the Human Authority / Governance approval boundary",
    ):
        assert marker in text


def test_check_19_context_memory_separation():
    text = _normalized(RECORD)
    for marker in (
        "context is not memory",
        "Current state and historical trace are separate",
        "Historical information may inform current state but may not silently overwrite it",
        "Memory may supply context but may not independently redefine current Goal",
    ):
        assert marker in text


def test_check_20_four_time_semantics():
    text = _normalized(RECORD)
    for marker in (
        "Event Time: when the external or internal event actually occurred",
        "Observation Time: when Aether or another observer perceived or obtained the event",
        "Recording Time: when the information entered an Aether record",
        "Decision Time: when Aether formed or authorized a conclusion",
    ):
        assert marker in text


def test_check_21_22_five_temporal_scopes_and_personal_timeline():
    text = _normalized(RECORD)
    for marker in (
        "Immediate Context: the current moment",
        "Execution Context: the duration of the current task or plan",
        "Personal Timeline: the temporally ordered history relevant to Aether's identity continuity",
        "Domain/Social Context: the external domain and social environment",
        "Long-term Context: identity continuity, memory aging, and growth",
        "reasoning scopes, not mandatory separate storage systems",
        "must not create a separate temporal agent",
        "Time provides context, not authority",
    ):
        assert marker in text


def test_check_23_24_hard_constraints_vs_soft_signals_no_weights():
    text = _normalized(RECORD)
    for marker in (
        "Hard constraints define the allowed decision space",
        "Soft decision signals rank options only inside that allowed space",
        "Hard constraints must never be overridden by optimization",
        "The Constitution",
        "Safety prohibitions",
        "identity integrity",
        "mandatory verification",
        "Resource hard limits",
        "No numerical weights and no universal scoring function are defined",
        "Minimum reversibility requirements where applicable",
        "greater reversibility may be a soft preference",
    ):
        assert marker in text


def test_check_25_thinking_proposes_governance_authorizes():
    text = _normalized(RECORD)
    for marker in (
        "Thinking proposes. Governance authorizes. Verification supplies evidence. "
        "Action executes only within authorization.",
        "The current deterministic Thinking Policy and the current Safety Stack remain unchanged",
    ):
        assert marker in text


def test_check_26_27_resource_observation_vs_governance_time_bounded():
    text = _normalized(RECORD)
    for marker in (
        "Resource Observation remains part of AetherOS Infrastructure",
        "explicitly distinct from the Execution Loop Observe stage",
        "does not authorize, allocate, select, terminate, or expand resources",
        "resource facts must be time-bounded",
        "Resource Observation reports; Resource Governance decides",
    ):
        assert marker in text


def test_check_28_background_continuity_bindings_and_no_new_authority():
    text = _normalized(RECORD)
    for marker in (
        "Core Coordination owns continuation state and task continuity",
        "Core Governance owns continuing authorization and constraints",
        "Time / AetherOS provide wake, expiry, scheduling, and timer mechanisms",
        "the originating goal",
        "the exact task",
        "the authoritative task-context identifier",
        "the Human Authority scope",
        "the wake condition",
        "the expiry",
        "the cancellation mechanism",
        "the checkpoint",
        "the verification criteria",
        "the audit trail",
        "It does not create a new goal or new authority",
        "extend expired authority",
        "retry indefinitely",
        "silently perform external actions",
        "reinterpret old permissions as permanent",
        "change completion criteria without authorization",
        "silently merge context into another task",
        "No scheduler and no background runtime is implemented by Milestone 86",
    ):
        assert marker in text


def test_check_29_economic_reasoning_vs_agency_no_payment_content():
    text = _normalized(RECORD)
    for marker in (
        "Economic Reasoning is an optional analysis capability",
        "Economic Agency is an optional execution capability",
        "must not define: wallets, tokens, autonomous earning, autonomous trading",
        "Economic Agency requires a separate future authorized architecture and safety milestone",
        "optional extensions cannot redefine the Core",
    ):
        assert marker in text


def test_check_30_31_constitution_unchanged_and_absent_rejected_article():
    constitution_text = _read(CONSTITUTION)
    assert constitution_text
    assert "**Version:** 0.2.0" in constitution_text
    rejected_article = "# 1" + "3. Runtime Application"
    assert rejected_article not in constitution_text
    record_text = _normalized(RECORD)
    assert "Constitution impact: NONE" in record_text
    assert "byte-identical" in record_text
    assert "no constitutional article is added" in record_text


def test_check_32_33_readme_clarification_verbatim_and_separate_agents_preserved():
    text = _read(README)
    assert README_ADDITION in text
    assert "Aether is not a collection of separate agents." in text
    assert text.index("## Project status") > text.index(README_ADDITION)


def test_check_34_35_architecture_diagram_markers_and_canonical_loop():
    text = _normalized(ARCHITECTURE)
    for marker in (
        "Constitution / Core Governance",
        "Authoritative Shared Cognitive Context",
        "Workflow / Policy proposes; Governance authorizes",
        "one selected current task context",
        "owned by Core Coordination",
        "The flow is not always linear.",
        "Aether may loop between Thinking, Memory, Verification, and Action until the task is complete or blocked.",
        CANONICAL_LOOP,
    ):
        assert marker in text
    assert "shared current state" not in text
    assert "The Identity organ is the anchor of that identity" not in text
    assert "not a second Identity component, not a second cognitive organ, and not a second authority source" in text
    assert "loads, represents, protects, and verifies that same continuous identity" in text


def test_check_36_37_version_030_and_supersession_clause():
    text = _read(ARCHITECTURE)
    assert "**Version:** 0.3.0" in text
    assert "**Status:** Foundational architecture" in text
    assert "**Depends on:** The Aether Constitution v0.2.0" in text
    assert SUPERSESSION_CLAUSE in text


def test_check_38_39_architecture_section_18_and_14_subsections():
    text = _read(ARCHITECTURE)
    assert "## 18. Architecture Evolution — Governance, Coordination, and AetherOS Infrastructure" in text
    for subsection in SECTION_18_SUBSECTIONS:
        assert subsection in text


def test_check_40_twenty_three_invariants_in_record_and_architecture():
    record_text = _normalized(RECORD)
    architecture_text = _normalized(ARCHITECTURE)
    for invariant in INVARIANTS:
        assert invariant in record_text
        assert invariant in architecture_text
    assert "Architecture invariants (23)" in architecture_text


def test_check_41_regression_locks_kept_separate():
    text = _normalized(RECORD)
    for marker in (
        "Regression locks (separate from the invariants)",
        "OpenAPI: 304 paths / 108 schemas",
        "8 @app routes / 23 include_router / zero direct /action/*",
        "600fd549588be7f536f704bc999be1987dcdf550225f2dc11dbf2fbf63ec2bcd",
        "Regression metrics are not substitutes for architecture invariants",
    ):
        assert marker in text


def test_check_42_milestone_85_boundary_record_remains_in_force():
    record_text = _normalized(RECORD)
    assert SUPERSESSION_CLAUSE in record_text
    assert M85_RECORD.exists()
    m85_text = _normalized(M85_RECORD)
    assert "Milestone 85 introduces no runtime capability" in m85_text


def test_check_43_44_no_implementation_or_runtime_claims():
    record_text = _read(RECORD)
    architecture_text = _read(ARCHITECTURE)
    for token in FORBIDDEN_DOC_TOKENS:
        assert token not in record_text
        assert token not in architecture_text
    for marker in (
        "No scheduler and no background runtime is implemented by Milestone 86",
        "Milestone 86 Adds No Runtime Capability",
    ):
        assert marker in record_text


def test_check_45_46_closure_rule_and_m87_no_auto_start():
    text = _normalized(RECORD)
    for marker in (
        "Milestone 86 is not considered closed until 86A Finalization is accepted",
        "The local 86A Build does not close Milestone 86",
        "does not start Milestone 87",
        "Milestone 87 may not start automatically",
        "Producer-proof gate",
        "Aggregator-proof gate",
        "Critic/Repair-proof gate",
    ):
        assert marker in text


def test_check_47_48_arch_49_and_74_placements():
    text = _read(ARCHITECTURE)
    assert "### 4.9 Temporal context and multi-timescale reasoning" in text
    assert "## 5" in text
    clarification = (
        "The items listed above are proposals, not authorizations. The Workflow and Policy Layer "
        "proposes workflows, risk framing, and resource needs; whether a proposed path is allowed "
        "is decided by Core Governance (section 18). Thinking proposes. Governance authorizes."
    )
    assert clarification in text
    assert "### 7.5 Future implementation" in text
    assert "### 4.8 Future implementation" in text
