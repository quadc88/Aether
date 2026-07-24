\# Aether



> A persistent digital intelligence that thinks, learns, verifies, and grows.



Aether is not a chatbot.



Aether is not an LLM.



Aether is not a collection of separate agents.



Aether is a single persistent digital intelligence with one evolving identity.



It is designed to:



\- think and plan;

\- build and use long-term memory;

\- learn from experience;

\- verify information before trusting it;

\- use tools when necessary;

\- discover or create new tools when existing tools are insufficient;

\- consult external LLMs as expert resources;

\- maintain a continuous identity while developing a unique personality through experience.



Different users may begin with the same Aether software, but their Aether will gradually become different through memory, knowledge, experience, and interaction.



\## Core principle



> Identity remains. Personality evolves.



\## Execution Loop

Every task Aether undertakes follows a structured loop designed to ensure verifiable outcomes, not just generated text.

### Target Execution Loop

```text
Receive Goal → Understand → Think → Plan → Act → Observe → Verify → Critic → Repair → Learn → Report
```

- Every task must define verifiable completion conditions.
- Aether must not end tasks only because an LLM or tool claims completion.
- After Act, Aether must Observe real system or world state.
- Verify checks observable evidence against the expected outcome.
- If verification fails, Critic analyzes failure and Repair updates the plan before looping again.
- Learn records useful experience for future tasks.
- Report explains the outcome and supporting evidence.

### Current Implemented Chat Loop

The current `/chat` endpoint implements a safe skeleton of this loop:

```text
Input → Perception → Identity Integrity Guard → Time → Working Memory → Risk Verification → Tool Suggestion → Thinking Policy → Policy Enforcement Gate → Approval Request Object → Timeline → Structured Response
```

Current safety constraints:
- `tool_execution_allowed` is always `false`.
- `tool_executed` is always `false`.
- The policy gate blocks execution by default.
- The approval request object is a pending review object only — it does not execute anything.
- No real approval workflow is active yet.
- No persistent approval queue exists yet.
- No automatic tool execution occurs.

Tools, models, and plugins are resources or organs Aether may use. They are not Aether itself. Aether maintains identity, memory, time, verification, policy, and action safety.

\## Project status



Aether is currently progressing through foundational milestones. Each milestone adds verified capability without compromising safety, identity, or the core architecture.

