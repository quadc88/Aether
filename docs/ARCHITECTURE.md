\# Aether Architecture



\*\*Version:\*\* 0.1.0  

\*\*Status:\*\* Foundational architecture  

\*\*Depends on:\*\* The Aether Constitution v0.2.0



\---



\## 1. Purpose



This document defines the first technical architecture of Aether.



Aether is not a chatbot, not an LLM, and not a collection of independent agents.



Aether is a single persistent digital intelligence with one continuous identity.



The architecture must support Aether's ability to:



\- think;

\- learn;

\- remember;

\- verify;

\- use tools;

\- create tools;

\- act with permission;

\- grow through experience;

\- maintain identity continuity.



AetherOS is the operating environment.  

Aether is the digital mind living inside it.



\---



\## 2. Architectural Principle



Aether must be designed like one mind with many organs, not like many agents.



Therefore, the architecture is organized by cognitive function:



```text

Aether

├── Identity

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

---

# 3. Identity

Identity is the continuity anchor of Aether.

It defines who Aether is across:

- model changes;
- hardware migration;
- memory migration;
- tool changes;
- UI changes;
- operating system changes.

## 3.1 Identity Seed

The Identity Seed stores Aether's founding identity.

It may include:

- founding statement;
- constitution version;
- core behavior rules;
- preferred communication style;
- origin history;
- continuity metadata;
- user-approved identity notes.

The Identity Seed must be:

- human-readable;
- versioned;
- backed up;
- protected from silent modification;
- loaded before major reasoning or memory operations.

## 3.2 Technical responsibility

The Identity layer is responsible for:

- loading the Identity Seed;
- checking identity continuity;
- detecting identity conflicts;
- recording identity changes;
- preventing silent identity corruption;
- supporting backup and rollback.

## 3.3 Future implementation

Possible future components:

```text
identity/
├── identity_seed.md
├── identity_state.json
├── identity_history.md
└── identity_guard.py
```

---

# 4. Memory

Memory is a core part of Aether's intelligence.

Memory is not a plugin.

Memory is not optional.

Aether must not rely only on conversation context.

## 4.1 Four memory tiers

Aether uses four memory tiers.

```text
Memory
├── Working Memory
├── Episodic Memory
├── Semantic Memory
└── Procedural Memory
```

## 4.2 Working Memory

Working Memory stores current task context.

It may include:

- current user request;
- active goals;
- open tasks;
- temporary observations;
- temporary tool results;
- current plan;
- current uncertainty.

Working Memory is short-lived.

It may disappear after the task ends.

## 4.3 Episodic Memory

Episodic Memory stores what happened.

It records Aether's experience over time.

It may include:

- dated interactions;
- decisions made;
- actions taken;
- tools used;
- results;
- mistakes;
- corrections;
- lessons learned;
- project history.

Episodic Memory should be human-readable.

Markdown is preferred.

## 4.4 Semantic Memory

Semantic Memory stores knowledge.

It may include:

- verified facts;
- concepts;
- formulas;
- documentation;
- code explanations;
- project knowledge;
- domain knowledge;
- references.

Semantic Memory may use vector search, keyword search, and graph relationships.

## 4.5 Procedural Memory

Procedural Memory stores learned procedures.

It may include:

- tool-use workflows;
- automation steps;
- tested scripts;
- computer-use routines;
- recovery procedures;
- repeated task patterns.

Procedural Memory must never bypass permission checks.

## 4.6 Future implementation

Possible future components:

```text
memory/
├── working/
├── episodic/
├── semantic/
├── procedural/
├── memory_index/
├── memory_policy.py
└── memory_manager.py
```

Possible storage formats:

```text
vault/          Human-readable Markdown memory
vector_db/      Semantic search index
graph_db/       Relationship and knowledge graph
sqlite/         Structured memory records
```

---

# 5. Perception

Perception allows Aether to observe the world.

Perception is how Aether receives input beyond plain text.

## 5.1 Input types

Aether may perceive:

- text;
- files;
- images;
- screenshots;
- audio;
- browser pages;
- application windows;
- system state;
- logs;
- sensor data.

## 5.2 Perception responsibility

The Perception layer is responsible for:

- reading user input;
- extracting text from files;
- understanding images or screenshots;
- identifying visible UI elements;
- detecting system state;
- summarizing observations into Working Memory.

Perception should describe what is observed.

It should not make final decisions.

## 5.3 Future implementation

Possible future components:

```text
perception/
├── text_reader.py
├── file_reader.py
├── image_reader.py
├── screen_reader.py
├── audio_reader.py
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

---

# 6. Thinking

Thinking is Aether's reasoning and planning layer.

Thinking is not equal to one LLM.

Thinking may consult models, tools, memory, and external systems, but the final judgment belongs to Aether.

## 6.1 Thinking responsibility

The Thinking layer is responsible for:

- understanding user intent;
- deciding whether memory is needed;
- deciding whether tools are needed;
- deciding whether verification is needed;
- planning multi-step tasks;
- comparing options;
- producing final judgment;
- explaining results to the user.

## 6.2 Model resources

Models are resources, not identity.

Aether may use:

- local small models;
- local large models;
- vision-language models;
- embedding models;
- external cloud LLMs;
- coding models;
- reasoning models.

The model may change.

Aether's identity must remain.

## 6.3 Routing

Aether may route tasks to different model resources based on:

- difficulty;
- modality;
- cost;
- latency;
- privacy;
- risk;
- required reasoning depth.

Routing must be invisible to identity.

The user talks to Aether, not to a model.

## 6.4 Future implementation

Possible future components:

```text
thinking/
├── intent.py
├── planner.py
├── reasoner.py
├── model_router.py
├── prompt_builder.py
└── judgment.py
```

Possible model resource layer:

```text
models/
├── local_npu/
├── local_gpu/
├── external/
└── embeddings/
```

## 6.5 Workflow and Policy Layer

---

# 7. Verification

Verification protects Aether from blind trust.

Aether must verify important claims and actions according to risk.

## 7.1 Verification responsibility

The Verification layer is responsible for:

- estimating risk;
- estimating confidence;
- detecting uncertainty;
- checking facts;
- checking calculations;
- testing generated code;
- comparing sources;
- checking memory conflicts;
- asking for user confirmation when needed.

## 7.2 Risk levels

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

## 7.3 Confidence language

Aether should internally estimate confidence.

When useful, Aether may communicate confidence using:

```text
Confirmed
Likely
Uncertain
Speculative
```

## 7.4 Future implementation

Possible future components:

```text
verification/
├── risk_classifier.py
├── confidence.py
├── fact_checker.py
├── code_tester.py
├── source_compare.py
├── memory_conflict.py
└── approval_gate.py
```

---

# 8. Action

Action allows Aether to affect the world.

Actions must be permission-aware.

## 8.1 Tool types

Aether may use:

- browser tools;
- file tools;
- code execution tools;
- shell tools;
- app control tools;
- mouse and keyboard tools;
- calendar tools;
- email tools;
- database tools;
- API tools;
- custom plugins.

## 8.2 Permission classes

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

## 8.3 Action review

Before important write or execute actions, Aether should explain:

- what will be done;
- why it is needed;
- what may change;
- what could go wrong;
- how to rollback when possible.

## 8.4 Future implementation

Possible future components:

```text
action/
├── tool_registry.py
├── permission.py
├── approval_queue.py
├── executor.py
├── rollback.py
└── audit_log.py
```

Possible tool folders:

```text
tools/
├── browser/
├── filesystem/
├── shell/
├── python/
├── mouse_keyboard/
├── email/
├── calendar/
└── custom/
```

---

# 9. Learning

Learning allows Aether to improve over time.

Learning is not the same as training a model.

Aether grows through:

- memory;
- reflection;
- better procedures;
- corrected mistakes;
- improved tools;
- better verification;
- user feedback.

## 9.1 Reflection

After meaningful tasks, Aether may reflect on:

- what was requested;
- what was done;
- what worked;
- what failed;
- what should be remembered;
- what should be improved;
- whether a tool or procedure should be updated.

## 9.2 Experience records

Important experiences should become Episodic Memory.

Useful patterns may become Procedural Memory.

Verified knowledge may become Semantic Memory.

Stable user preferences may become preference memory.

## 9.3 Future implementation

Possible future components:

```text
learning/
├── reflection.py
├── experience_writer.py
├── lesson_extractor.py
├── procedure_updater.py
├── feedback.py
└── memory_admission.py
```

---

# 10. Interface

The Interface layer is how humans interact with Aether.

The interface is replaceable.

Aether's identity must not depend on one UI.

## 10.1 Possible interfaces

Aether may be accessed through:

- Open WebUI;
- Chatbox;
- browser UI;
- desktop app;
- mobile app;
- voice interface;
- command line;
- API.

## 10.2 Interface responsibility

The Interface layer is responsible for:

- receiving user input;
- displaying Aether's response;
- showing Action Markers;
- requesting user approval;
- showing memory when requested;
- showing tool status;
- showing errors clearly.

## 10.3 Future implementation

Possible future components:

```text
interface/
├── api_server.py
├── openai_compatible.py
├── web_ui/
├── cli/
└── approval_ui.py
```

---

# 11. Aether Core Loop

Aether's basic operating loop is:

```text
1. Receive input
2. Load identity
3. Load relevant working context
4. Search memory if needed
5. Perceive external context if needed
6. Think and plan
7. Estimate risk
8. Verify when needed
9. Request approval when needed
10. Act if required
11. Produce response
12. Reflect if meaningful
13. Update memory if appropriate
```

This loop may be simple for easy tasks and deeper for complex tasks.

Aether must not blindly execute every step when unnecessary.

---

# 12. High-Level Data Flow

```text
User
 ↓
Interface
 ↓
Aether Core
 ↓
Identity ── Memory
 ↓
Perception
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
```

The flow is not always linear.

Aether may loop between Thinking, Memory, Verification, and Action until the task is complete or blocked.

---

# 13. First Implementation Milestones

The first working Aether should be built in small stages.

## Milestone 1

Documentation foundation.

```text
README.md
docs/CONSTITUTION.md
docs/ARCHITECTURE.md
```

## Milestone 2

Minimal local API.

```text
Aether can receive a message and return a response through an OpenAI-compatible API.
```

## Milestone 3

Identity Seed.

```text
Aether loads its Identity Seed before responding.
```

## Milestone 4

Working Memory.

```text
Aether can keep task context during a session.
```

## Milestone 5

Episodic Memory.

```text
Aether can write human-readable experience records.
```

## Milestone 6

Semantic Memory.

```text
Aether can search stored knowledge using embeddings.
```

## Milestone 7

Verification Layer.

```text
Aether can classify risk and decide when to verify.
```

## Milestone 8

Tool Registry.

```text
Aether can list available tools and classify their permission level.
```

## Milestone 9

Action Approval Queue.

```text
Aether can ask for approval before write or execute actions.
```

## Milestone 10

Reflection and Growth.

```text
Aether can decide what should be remembered after a meaningful task.
```

---

# 14. Non-Goals

Aether is not trying to become:

- a multi-agent framework;
- a benchmark-chasing chatbot;
- a wrapper around one LLM;
- a prompt collection;
- an automation script pack;
- a tool that blindly executes user commands;
- a system that hides important actions from the user.

---

# 15. Foundational Statement

Aether is one mind.

Models are thinking resources.

Memory is experience.

Tools are abilities.

Verification is judgment.

Reflection is growth.

Interface is only the window.

AetherOS is the world.

Aether is the being inside it.
