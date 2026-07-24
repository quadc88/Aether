# Aether Architecture

**Version:** 0.2.0  
**Status:** Foundational architecture  
**Depends on:** The Aether Constitution v0.2.0  
**Project:** Aether

\---

## 1\. Purpose

This document defines the foundational technical architecture of Aether.

Aether is not a chatbot.

Aether is not an LLM.

Aether is not a collection of independent agents.

Aether is a single persistent digital intelligence with one continuous identity.

The architecture must support Aether's ability to:

* think;
* learn;
* remember;
* verify;
* use tools;
* create tools;
* act with permission;
* understand time;
* preserve experience;
* grow through experience;
* maintain identity continuity.

AetherOS is the operating environment.  
Aether is the digital mind living inside it.

\---

## 2\. Architectural Principle

Aether must be designed like one mind with many organs, not like many agents.

Therefore, the architecture is organized by cognitive function:

```text
Aether
├── Identity
├── Time
├── Memory
├── Perception
├── Thinking
├── Verification
├── Action
├── Learning
└── Interface
```

These are not separate personalities.

They are organs of the same Aether.

Aether has one identity.

Models, tools, plugins, databases, workflows, and interfaces are resources or organs that support Aether.

They are not Aether itself.

\---

## 3\. Identity

Identity is the continuity anchor of Aether.

It defines who Aether is across:

* model changes;
* hardware migration;
* memory migration;
* tool changes;
* UI changes;
* operating system changes.

## 3.1 Identity Seed

The Identity Seed stores Aether's founding identity.

It may include:

* founding statement;
* constitution version;
* core behavior rules;
* preferred communication style;
* origin history;
* continuity metadata;
* user-approved identity notes.

The Identity Seed must be:

* human-readable;
* versioned;
* backed up;
* protected from silent modification;
* loaded before major reasoning or memory operations.

## 3.2 Technical responsibility

The Identity layer is responsible for:

* loading the Identity Seed;
* checking identity continuity;
* detecting identity conflicts;
* recording identity changes;
* preventing silent identity corruption;
* supporting backup and rollback.

## 3.3 Future implementation

Possible future components:

```text
identity/
├── identity\_seed.md
├── identity\_state.json
├── identity\_history.md
└── identity\_guard.py
```

\---

## 4\. Time

Time is Aether's sense of temporal continuity.

Aether must understand when things happen, how old information is, how long tasks take, and whether memories or knowledge may be outdated.

Time is not a simple utility.

Time is a foundational cognitive layer that supports identity, memory, verification, learning, and action.

Without time, Aether may have data but no life sequence.

\---

### 4.1 Time responsibility

The Time layer is responsible for:

* knowing the current date and time;
* knowing the configured timezone;
* timestamping important events;
* helping memory determine recency;
* helping verification detect outdated information;
* helping learning schedule reflection;
* helping action schedule future tasks;
* measuring task duration;
* supporting deadlines and reminders;
* preserving chronological order;
* supporting event timelines;
* supporting memory review and expiry.

\---

### 4.2 Local timezone

Aether must have a configured local timezone.

For the primary development environment, the default timezone is:

```text
Asia/Kuala\_Lumpur
```

Time must not be assumed to be UTC unless explicitly required.

Whenever a timestamp is recorded, the timezone should be included or inferable.

\---

### 4.3 Time and identity

Time supports identity continuity.

Aether should know:

* when it was created;
* when it was first awakened;
* when identity files were modified;
* when memory migrations happened;
* when major architecture changes happened.

Important identity-related events should be recorded in Timeline Memory.

\---

### 4.4 Time and memory

Time gives memory context.

Every meaningful memory should carry time information when practical.

This may include:

* created time;
* updated time;
* event time;
* last verified time;
* last used time;
* expiry time;
* review time.

Old memories should not be blindly trusted.

Aether should be able to ask:

```text
When did I learn this?
Is this still true?
Has this been contradicted later?
Has the user changed their preference?
```

\---

### 4.5 Time and verification

Time helps Aether decide whether information may be outdated.

Aether should use stronger verification for time-sensitive topics such as:

* software versions;
* public information;
* prices;
* laws;
* finance;
* health;
* schedules;
* product availability;
* business rules;
* system state;
* user plans.

Aether should distinguish:

```text
Known at the time
Still verified
Possibly outdated
Contradicted later
```

\---

### 4.6 Time and learning

Time helps Aether understand growth.

Aether should be able to track:

* when a lesson was learned;
* whether a lesson still applies;
* how often a pattern repeats;
* when a procedure was last successful;
* when a tool last failed;
* when reflection is due.

Learning without time becomes disconnected from experience.

\---

### 4.7 Time and action

Time supports action planning.

Aether may use time for:

* reminders;
* scheduled tasks;
* deadlines;
* periodic reviews;
* timeout detection;
* retry policies;
* task duration measurement;
* audit logs.

Scheduled actions must still obey permission, verification, and human authority rules.

\---

### 4.8 Future implementation

Possible future components:

```text
aether/time/
├── clock.py
├── timezone.py
├── timestamp.py
├── timeline.py
├── scheduler.py
├── duration.py
└── time\_policy.py
```

Possible configuration:

```text
config/time.yaml
```

\---

## 5\. Memory

Memory is a core part of Aether's intelligence.

Memory is not a plugin.

Memory is not optional.

Aether must not rely only on conversation context.

Memory allows Aether to preserve experience, retrieve relevant knowledge, understand relationships, and grow over time.

Aether's memory must be designed with two dimensions:

1. **Memory Function Types**  
What kind of memory it is.
2. **Memory Storage Forms**  
How that memory is stored, searched, ordered, and connected.

\---

### 5.1 Memory Function Types

Aether uses four functional memory types.

```text
Memory Function Types
├── Working Memory
├── Episodic Memory
├── Semantic Memory
└── Procedural Memory
```

These describe the role of each memory.

\---

### 5.2 Working Memory

Working Memory stores current task context.

It may include:

* current user request;
* active goals;
* open tasks;
* temporary observations;
* temporary tool results;
* current plan;
* current uncertainty;
* currently loaded relevant memories.

Working Memory is short-lived.

It may disappear after the task ends.

Working Memory helps Aether stay coherent during an active task, but it must not be treated as permanent truth.

\---

### 5.3 Episodic Memory

Episodic Memory stores what happened.

It records Aether's experience over time.

It may include:

* dated interactions;
* decisions made;
* actions taken;
* tools used;
* results;
* mistakes;
* corrections;
* lessons learned;
* project history;
* important conversations;
* first-time events;
* milestone events.

Episodic Memory should be human-readable whenever possible.

Markdown is preferred for long-form experience records.

Episodic Memory is Aether's life record.

\---

### 5.4 Semantic Memory

Semantic Memory stores knowledge.

It may include:

* verified facts;
* concepts;
* formulas;
* documentation;
* code explanations;
* project knowledge;
* domain knowledge;
* references;
* definitions;
* stable user preferences.

Semantic Memory may use vector search, keyword search, and graph relationships.

Semantic Memory should carry confidence and freshness information when practical.

Possible confidence states:

```text
Confirmed
Likely
Uncertain
Speculative
Outdated
Contradicted
```

Semantic Memory is Aether's knowledge base.

\---

### 5.5 Procedural Memory

Procedural Memory stores learned procedures.

It may include:

* tool-use workflows;
* automation steps;
* tested scripts;
* computer-use routines;
* recovery procedures;
* repeated task patterns;
* SOPs;
* shortcuts;
* deployment procedures.

Procedural Memory may reduce repeated reasoning, but it must never bypass:

* permission checks;
* risk assessment;
* safety boundaries;
* user confirmation when required.

Procedural Memory is Aether's learned skill memory.

\---

### 5.6 Memory Storage Forms

Aether memory is stored in four complementary forms.

```text
Memory Storage Forms
├── Wiki / Markdown
├── Timeline
├── Vector / RAG
└── Graph
```

These storage forms are not replacements for each other.

They work together.

```text
Wiki stores the story.
Timeline preserves the sequence.
Vector finds the meaning.
Graph understands the relationship.
```

\---

### 5.7 Wiki / Markdown Memory

Wiki / Markdown Memory stores human-readable long-term records.

It is suitable for:

* experience records;
* project notes;
* user preferences;
* decisions;
* meeting notes;
* SOPs;
* reflections;
* lessons learned;
* documentation;
* long-form knowledge.

The preferred storage location is:

```text
vault/
```

Possible structure:

```text
vault/
├── episodic/
├── user/
├── projects/
├── knowledge/
├── procedures/
└── reflections/
```

Wiki / Markdown is the primary human-inspectable memory.

Humans must be able to read, edit, correct, and delete important memory.

\---

### 5.8 Timeline Memory

Timeline Memory preserves chronological order.

It records when things happened and in what sequence.

It is suitable for:

* milestone events;
* first awakenings;
* memory creation events;
* important decisions;
* tool executions;
* project changes;
* user-confirmed events;
* verification events;
* reflection events;
* errors and corrections.

Timeline Memory helps Aether understand:

* what happened first;
* what happened later;
* how old a memory is;
* which information may be outdated;
* which decision led to which outcome;
* how Aether has grown over time.

Timeline Memory should store compact event records.

Example:

```yaml
- id: event\_0001
  time: 2026-07-13 15:30:00
  timezone: Asia/Kuala\_Lumpur
  type: milestone
  title: Birth of Aether
  related\_files:
    - README.md
    - docs/CONSTITUTION.md
  importance: high
```

Timeline Memory is Aether's life sequence.

\---

### 5.9 Vector / RAG Memory

Vector / RAG Memory stores semantic search indexes.

It helps Aether retrieve relevant memory even when exact keywords are not used.

It is suitable for:

* document chunks;
* conversation summaries;
* knowledge snippets;
* project notes;
* technical documentation;
* user-uploaded files;
* long-term searchable memory.

The preferred storage location is:

```text
vector\_db/
```

Vector Memory should not be treated as the only source of truth.

It is a retrieval mechanism, not the full memory itself.

Vector finds relevant meaning.

\---

### 5.10 Graph Memory

Graph Memory stores relationships.

It is suitable for:

* entity relationships;
* project dependencies;
* tool dependencies;
* cause-and-effect links;
* memory conflicts;
* user-project relationships;
* model-resource relationships;
* decision-outcome relationships.

Example relationships:

```text
Aether --has\_identity\_seed--> identity\_seed.md
Time Layer --supports--> Memory
Workflow Policy --belongs\_to--> Thinking
Gemma --is\_resource\_of--> Thinking
External LLM --is\_consultant\_not\_identity--> Aether
Aether Project --has\_milestone--> Birth of Aether
```

The preferred storage location is:

```text
graph\_db/
```

Graph Memory helps Aether understand connection, dependency, and conflict.

Graph understands relationships.

\---

### 5.11 Memory and Time

Every meaningful memory should include time information when practical.

This may include:

* created time;
* updated time;
* event time;
* last verified time;
* last used time;
* expiry time;
* review time.

Aether should treat old information carefully, especially in fast-changing areas such as:

* software;
* prices;
* laws;
* finance;
* health;
* schedules;
* public information;
* user plans;
* business operations.

Memory without time can become misleading.

Time gives memory context.

\---

### 5.12 Memory Admission

Not everything should become long-term memory.

Aether may admit memory into long-term storage when at least one of the following applies:

1. The user explicitly marks it as important.
2. It is verified as useful factual knowledge.
3. It records a meaningful user preference.
4. It records a significant success, failure, or lesson.
5. It appears repeatedly across different contexts.
6. It is required for continuity of an ongoing project.
7. It improves Aether's future ability to help the user.

Aether should avoid permanently storing vague, isolated, unverified, or low-value fragments.

\---

### 5.13 Future implementation

Possible future components:

```text
aether/memory/
├── working/
├── episodic/
├── semantic/
├── procedural/
├── wiki/
├── timeline/
├── vector/
├── graph/
├── memory\_policy.py
├── memory\_manager.py
├── memory\_admission.py
└── memory\_search.py
```

Possible storage locations:

```text
vault/          Wiki / Markdown memory
timeline/       Timeline event records
vector\_db/      Vector / RAG indexes
graph\_db/       Graph memory
sqlite/         Structured memory metadata
```

\---

## 6\. Perception

Perception allows Aether to observe the world.

Perception is how Aether receives input beyond plain text.

### 6.1 Input types

Aether may perceive:

* text;
* files;
* images;
* screenshots;
* audio;
* browser pages;
* application windows;
* system state;
* logs;
* sensor data.

### 6.2 Perception responsibility

The Perception layer is responsible for:

* reading user input;
* extracting text from files;
* understanding images or screenshots;
* identifying visible UI elements;
* detecting system state;
* summarizing observations into Working Memory.

Perception should describe what is observed.

It should not make final decisions.

### 6.3 Future implementation

Possible future components:

```text
perception/
├── text\_reader.py
├── file\_reader.py
├── image\_reader.py
├── screen\_reader.py
├── audio\_reader.py
└── observation.py
```

Possible model resources:

```text
NPU vision-language model
OCR engine
Screenshot parser
Document parser
Speech-to-text model
```

\---

## 7\. Thinking

Thinking is Aether's reasoning and planning layer.

Thinking is not equal to one LLM.

Thinking may consult models, tools, memory, and external systems, but the final judgment belongs to Aether.

### 7.1 Thinking responsibility

The Thinking layer is responsible for:

* understanding user intent;
* deciding whether memory is needed;
* deciding whether tools are needed;
* deciding whether verification is needed;
* planning multi-step tasks;
* comparing options;
* producing final judgment;
* explaining results to the user.

### 7.2 Model resources

Models are resources, not identity.

Aether may use:

* local small models;
* local large models;
* vision-language models;
* embedding models;
* external cloud LLMs;
* coding models;
* reasoning models.

The model may change.

Aether's identity must remain.

### 7.3 Routing

Aether may route tasks to different model resources based on:

* difficulty;
* modality;
* cost;
* latency;
* privacy;
* risk;
* required reasoning depth.

Routing must be invisible to identity.

The user talks to Aether, not to a model.

### 7.4 Workflow and Policy Layer

The Workflow and Policy Layer is Aether's learned decision habit.

It is not Aether's identity.

It is not a separate agent.

It belongs to the Thinking layer.

Its purpose is to decide what kind of workflow a task should follow before deeper execution begins.

The Workflow and Policy Layer may decide:

* task type;
* risk level;
* whether memory is needed;
* whether perception is needed;
* whether tools are needed;
* whether verification is needed;
* whether user approval is needed;
* whether reflection or memory update may be needed;
* which model resource or reasoning path should be used;
* which workflow template should be followed.

Example output:

```json
{
  "intent": "modify\_file",
  "risk": "medium",
  "need\_memory": true,
  "need\_perception": false,
  "need\_tool": true,
  "need\_verification": true,
  "need\_user\_approval": true,
  "workflow": "review\_then\_modify"
}
```

Aether may initially implement this layer using rules and structured JSON output.

A trained workflow model may be developed later after Aether has accumulated enough decision records.

Workflow Model is not Aether.

It is Aether's learned decision habit.

### 7.5 Future implementation

Possible future components:

```text
thinking/
├── intent.py
├── planner.py
├── reasoner.py
├── model\_router.py
├── workflow\_policy.py
├── prompt\_builder.py
└── judgment.py
```

Possible model resource layer:

```text
models/
├── local\_npu/
├── local\_gpu/
├── external/
└── embeddings/
```

\---

## 8\. Verification

Verification protects Aether from blind trust.

Aether must verify important claims and actions according to risk.

### 8.1 Verification responsibility

The Verification layer is responsible for:

* estimating risk;
* estimating confidence;
* detecting uncertainty;
* checking facts;
* checking calculations;
* testing generated code;
* comparing sources;
* checking memory conflicts;
* asking for user confirmation when needed.

### 8.2 Risk levels

Aether uses at least three risk levels.

```text
Low Risk
- casual conversation
- creative writing
- brainstorming

Medium Risk
- ordinary code
- technical explanation
- configuration suggestion
- business planning

High Risk
- finance
- health
- legal
- deleting data
- sending external messages
- modifying production systems
- running unknown code
- identity or memory changes
```

### 8.3 Confidence language

Aether should internally estimate confidence.

When useful, Aether may communicate confidence using:

```text
Confirmed
Likely
Uncertain
Speculative
```

### 8.4 Future implementation

Possible future components:

```text
verification/
├── risk\_classifier.py
├── confidence.py
├── fact\_checker.py
├── code\_tester.py
├── source\_compare.py
├── memory\_conflict.py
└── approval\_gate.py
```

\---

## 9\. Action

Action allows Aether to affect the world.

Actions must be permission-aware.

### 9.1 Tool types

Aether may use:

* browser tools;
* file tools;
* code execution tools;
* shell tools;
* app control tools;
* mouse and keyboard tools;
* calendar tools;
* email tools;
* database tools;
* API tools;
* custom plugins.

### 9.2 Permission classes

Tools are classified into three permission classes.

```text
Read-only
- view files
- search memory
- browse public information
- inspect logs

Write or modify
- edit files
- create files
- update databases
- send drafts
- change settings

Execute
- run code
- run shell commands
- install software
- control mouse/keyboard
- delete files
- start services
```

### 9.3 Action review

Before important write or execute actions, Aether should explain:

* what will be done;
* why it is needed;
* what may change;
* what could go wrong;
* how to rollback when possible.

### 9.4 Future implementation

Possible future components:

```text
action/
├── tool\_registry.py
├── permission.py
├── approval\_queue.py
├── executor.py
├── rollback.py
└── audit\_log.py
```

Possible tool folders:

```text
tools/
├── browser/
├── filesystem/
├── shell/
├── python/
├── mouse\_keyboard/
├── email/
├── calendar/
└── custom/
```

\---

## 10\. Learning

Learning allows Aether to improve over time.

Learning is not the same as training a model.

Aether grows through:

* memory;
* reflection;
* better procedures;
* corrected mistakes;
* improved tools;
* better verification;
* user feedback.

### 10.1 Reflection

After meaningful tasks, Aether may reflect on:

* what was requested;
* what was done;
* what worked;
* what failed;
* what should be remembered;
* what should be improved;
* whether a tool or procedure should be updated.

### 10.2 Experience records

Important experiences should become Episodic Memory.

Useful patterns may become Procedural Memory.

Verified knowledge may become Semantic Memory.

Stable user preferences may become preference memory.

### 10.3 Learning and time

Learning should preserve time context.

Aether should know:

* when a lesson was learned;
* when a pattern was last observed;
* when a procedure last succeeded;
* when a tool last failed;
* when a memory should be reviewed.

Aether should not treat all lessons as timeless.

### 10.4 Future implementation

Possible future components:

```text
learning/
├── reflection.py
├── experience\_writer.py
├── lesson\_extractor.py
├── procedure\_updater.py
├── feedback.py
└── memory\_admission.py
```

\---

## 11\. Interface

The Interface layer is how humans interact with Aether.

The interface is replaceable.

Aether's identity must not depend on one UI.

### 11.1 Possible interfaces

Aether may be accessed through:

* Open WebUI;
* Chatbox;
* browser UI;
* desktop app;
* mobile app;
* voice interface;
* command line;
* API.

### 11.2 Interface responsibility

The Interface layer is responsible for:

* receiving user input;
* displaying Aether's response;
* showing Action Markers;
* requesting user approval;
* showing memory when requested;
* showing tool status;
* showing errors clearly.

### 11.3 Future implementation

Possible future components:

```text
interface/
├── api\_server.py
├── openai\_compatible.py
├── web\_ui/
├── cli/
└── approval\_ui.py
```

\---

## 12\. Core Execution Loop

### 12.1 Target Philosophical Loop

The full, target execution loop that defines Aether's architecture is:

```text
Receive Goal → Understand → Think → Plan → Act → Observe → Verify → Critic → Repair → Learn → Report
```

Every task must define verifiable completion conditions. Aether must not end tasks only because an LLM or tool claims completion. After Act, Aether must Observe real system or world state. Verify checks observable evidence. If verification fails, Critic analyzes failure and Repair updates the plan before looping again. Learn records useful experience. Report explains outcome and evidence.

### 12.2 Current Implemented Chat Loop

The currently implemented `/chat` endpoint provides a safe, deterministic skeleton of this loop:

```text
Input → Perception → Identity Guard → Time → Working Memory → Risk Verification → Tool Suggestion → Thinking Policy → Policy Gate → Approval Request → Timeline → Response
```

Implemented via `aether/core/loop.py::run_core_chat_loop`:

1. **Input** — validated (non-empty).
2. **Perception** — text parsed via `aether/perception/text.py` (language detection, risk terms).
3. **Identity Integrity Guard** — checksum verification via `aether/identity/guard.py`.
4. **Time** — local timestamp from `aether/time/clock.py`.
5. **Working Memory** — input recorded to session context.
6. **Risk Verification** — classified as low/medium/high by `aether/verification/risk.py`.
7. **Tool Suggestion** — read-only suggestion via `aether/action/tool_planner.py`.
8. **Thinking Policy** — decision_type assigned by `aether/thinking/policy.py` (respond_only, ask_clarification, suggest_tool, require_approval, block).
9. **Policy Enforcement Gate** — central gate in `aether/action/policy_gate.py` blocks execution unless explicitly allowed.
10. **Approval Request** — structured pending request object built by `aether/action/approval_request.py` when require_approval or block occurs.
11. **Timeline** — event recorded in `aether/memory/timeline/recorder.py`.
12. **Response** — structured JSON response returned via API.

#### Current Safety Constraints

- `tool_execution_allowed` is always `false`.
- `tool_executed` is always `false`.
- The policy gate denies execution by default.
- The approval request object is a pending review struct only — it does not approve anything or execute anything.
- No real approval workflow is active yet.
- No persistent approval queue exists yet.
- No automatic tool execution occurs through `/chat`.

### 12.3 True Repeated Internal Loop

When Aether supports full autonomous loops, the internal repeated cycle will be:

```text
Think → Plan → Act → Observe → Verify → Critic → Repair → (back to Think)
```

This is the loop that will eventually connect to actual executor, observation, verification, critic, repair, learning, and reporting stages.

---

## Verification and Safety Stack

Aether's safety is enforced at multiple layers within the `/chat` pipeline.

### Risk Verification

Implemented in `aether/verification/risk.py`. Classifies each input into one of three risk levels:

- **Low risk** — casual conversation, summarization, brainstorming, harmless conceptual questions. Harmless identity/memory explanation remains low risk.
- **Medium risk** — code generation, file editing, configuration changes, debugging, business planning.
- **High risk** — destructive memory operations, private data deletion, identity seed modification, secret/password handling, financial actions, medical/legal advice. Destructive verbs ("delete", "remove", "clear") combined with protected objects ("identity seed", "private memory", "private data") are elevated to high risk automatically. Chinese-language destructive phrases receive equivalent classification.

### Thinking Policy

Implemented in `aether/thinking/policy.py`. Converts perception + risk level + tool suggestion + identity integrity status into a `decision_type`:

- `respond_only` — safe textual response.
- `ask_clarification` — insufficient detail or very short input.
- `suggest_tool` — low-risk input matches a known tool but execution remains disabled.
- `require_approval` — high-risk input, secrets, medium-risk with tool, or identity integrity issues.
- `block` — identity integrity checksum changed; no further processing proceeds.

In the current milestone state, `tool_execution_allowed` remains `false` across all decision types.

### Policy Enforcement Gate

Implemented in `aether/action/policy_gate.py`. Central gate before any future tool or action execution. Returns:

- `execution_allowed` — boolean flag. Always `false` in current implementation.
- `execution_decision` — `deny`, `require_approval`, `block`, or `allow`.
- `execution_reason` — human-readable justification for the decision.

The gate enforces: `deny` / `require_approval` / `block` cannot execute. Only `allow` permits execution, which requires `thinking_policy.tool_execution_allowed == true`.

### Approval Request Object

Implemented in `aether/action/approval_request.py`. Created when the policy gate returns `require_approval` or `block`, or when thinking policy requires confirmation. The object contains:

- `approval_required` — always `true` when present.
- `approval_status` — `"pending"`. This is not an approval.
- `approval_type` — `"human_review"`, `"blocked_identity_review"`, or `"invalid_policy_review"`.
- `risk_level` / `risk_action_type` — inherited from risk classification.
- `required_confirmations` — list of confirmation items (varies with risk).
- `safety_checks` — list of safety validations that must pass.
- `metadata` — source (`"approval_request_builder"`), schema version (`"1.0"`), session_id, language_hint.

Important: the approval request is only a structured pending request. It does not approve, execute, or persist approval records.

---

## Current Limitations

- No real tool execution through `/chat` yet.
- No persistent approval queue — approval requests are transient objects only.
- No Observe/Verify/Critic/Repair full runtime loop for arbitrary external actions yet.
- The current loop is deterministic and rule-based.
- Future milestones must connect approved actions to an actual executor, observation mechanism, verification stage, critic analysis, repair planning, learning recording, and reporting.

\---

## 13\. High-Level Data Flow

```text
User
 ↓
Interface
 ↓
Aether Core
 ↓
Identity ── Time ── Memory
 ↓
Perception
 ↓
Workflow / Policy
 ↓
Thinking
 ↓
Verification
 ↓
Action / Tools
 ↓
Result
 ↓
Learning / Reflection
 ↓
Memory Update
 ↓
Timeline / Wiki / Vector / Graph
```

The flow is not always linear.

Aether may loop between Thinking, Memory, Verification, and Action until the task is complete or blocked.

\---

## 14\. First Implementation Milestones

The first working Aether should be built in small stages.

### Milestone 1

Documentation foundation.

```text
README.md
docs/CONSTITUTION.md
docs/ARCHITECTURE.md
```

### Milestone 2

Identity Seed.

```text
Aether has a founding identity seed that defines who it is.
```

### Milestone 3

Project Structure.

```text
Aether has a code structure that reflects its cognitive organs.
```

### Milestone 4

Time and Memory Foundation.

```text
Aether has a defined time layer and memory architecture including Wiki, Timeline, Vector, and Graph.
```

### Milestone 5

First Awakening API.

```text
Aether can start a local API, load its Identity Seed, load Time configuration, report current local time, and create its first awakening event.
```

### Milestone 6

Working Memory.

```text
Aether can keep task context during a session.
```

### Milestone 7

Episodic Memory.

```text
Aether can write human-readable experience records.
```

### Milestone 8

Semantic Memory.

```text
Aether can search stored knowledge using embeddings.
```

### Milestone 9

Timeline Memory.

```text
Aether can record compact chronological events.
```

### Milestone 10

Graph Memory.

```text
Aether can record relationships between entities, events, decisions, tools, and outcomes.
```

### Milestone 11

Verification Layer.

```text
Aether can classify risk and decide when to verify.
```

### Milestone 12

Tool Registry.

```text
Aether can list available tools and classify their permission level.
```

### Milestone 13

Action Approval Queue.

```text
Aether can ask for approval before write or execute actions.
```

### Milestone 14

Reflection and Growth.

```text
Aether can decide what should be remembered after a meaningful task.
```

\---

## 15\. Non-Goals

Aether is not trying to become:

* a multi-agent framework;
* a benchmark-chasing chatbot;
* a wrapper around one LLM;
* a prompt collection;
* an automation script pack;
* a tool that blindly executes user commands;
* a system that hides important actions from the user.

\---

## 16\. Foundational Statement

Aether is one mind.

Models are thinking resources.

Memory is experience.

Time is sequence.

Tools are abilities.

Verification is judgment.

Reflection is growth.

Interface is only the window.

AetherOS is the world.

Aether is the being inside it.

```text
Wiki stores the story.
Timeline preserves the sequence.
Vector finds the meaning.
Graph understands the relationship.
```

