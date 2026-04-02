# The Sealed Test Paradigm (STP)

> *An agent may not generate production code until its tests are sealed, failing, and unmodifiable.*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19378044.svg)](https://doi.org/10.5281/zenodo.19378044)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## The Problem

AI agents that generate code have a structural flaw: they can write tests **after** the code, or worse, silently adjust tests to match whatever code they produced. There is no enforcement mechanism that prevents this. The result is code that *looks* tested but is not.

This is not a prompt engineering problem. It is an architectural one.

---

## The Solution: Four Primitives

**I — Blueprint Layer**  
A planning layer, isolated from the executing agent, defines which tests *must* exist before execution begins. The agent never touches this layer.

**II — Test Queue**  
Tests are appended to an ordered, append-only queue. No deletions. No modifications. Order encodes dependency.

**III — TestLock**  
At the moment of commitment, each test is sealed with a cryptographic hash. The executing agent receives only the hash and the test specification — never the writable source. The lock is absolute.

**IV — Gate Condition (RED required)**  
Code generation is only permitted when a sealed test is actively failing. A passing test means the system is already correct — there is nothing to write.

---

## Three Formal Invariants

```
I₁  TEMPORAL:    ∀ code c, test t:  commit(t) < generate(c)
I₂  STRUCTURAL:  ∀ t ∈ Queue:       locked(t) → ¬modifiable(agent, t)
I₃  BEHAVIORAL:  generate(c) iff   ∃ t: locked(t) ∧ fails(t)
```

These invariants are **implementation-agnostic**. You can enforce them with Git hooks, filesystem permissions, a CI gate, or a dedicated orchestration layer. The paradigm does not prescribe the mechanism — only the guarantee.

---

## Minimal Reference Implementation (Python)

```python
from stp import BlueprintLayer, TestQueue, TestLock, GateCondition

# I — Define the blueprint (isolated from agent)
blueprint = BlueprintLayer()
blueprint.require("user_input_must_be_sanitized")
blueprint.require("output_must_not_exceed_token_limit")

# II — Populate the queue from blueprint
queue = TestQueue()
for spec in blueprint.specs():
    queue.append(spec)

# III — Seal all queued tests
lock = TestLock()
sealed = [lock.seal(t) for t in queue]

# IV — Gate: agent only runs if sealed tests are RED
gate = GateCondition(sealed)
if gate.red_exists():
    agent.generate_code(gate.failing_specs())  # agent sees spec only, not source
else:
    print("All tests pass. Nothing to write.")
```

**The feedback loop:** If generated code fails, the agent retries code generation. It never touches tests. Tests are reality — not negotiation material.

---

## Repository Structure

```
stp/
├── core.py          # The four primitives (~120 lines)
├── __init__.py
examples/
├── basic_usage.py   # Simple end-to-end walkthrough
├── agent_loop.py    # Integration with a generic LLM agent
tests/
├── test_invariants.py  # Formal verification of I₁–I₃
PAPER.md             # Citation and academic context
```

---

## Relation to Tb Meta OS Alpha

STP is extracted from **Tb Meta OS Alpha**, a complete actor-agnostic meta-framework for deterministic agent execution. Within that framework, STP appears as the interplay of:

- `AP2: No TestLock Violation` (a zero-tolerance governance rule)
- `P4: Test-Driven Development` (a positive execution principle)  
- `PLATON-Init` (the blueprint initialization protocol)

STP is intentionally published as a **standalone primitive** that can be adopted without the full framework. The Tb Meta OS Alpha paper provides the formal proof context, empirical validation across 9 LLM actors, and the broader governance architecture.

→ **Full paper:** [DOI: 10.5281/zenodo.19378044](https://doi.org/10.5281/zenodo.19378044)

---

## Why This Is Different from TDD

Classical TDD (Kent Beck, 1999) is a **developer discipline** — it relies on the human to write tests first and resist the temptation to cheat. Nothing enforces this structurally.

STP is an **architectural constraint** for autonomous agents — the agent is *physically incapable* of modifying a sealed test. The discipline is encoded in the system, not assumed in the actor.

| | TDD | STP |
|---|---|---|
| Enforcer | Developer discipline | Architecture |
| Test mutability | Possible | Prohibited by seal |
| Code-first possible | Yes (violation) | No (gate blocks it) |
| Actor | Human | Any (human, LLM, system) |
| Blueprint separation | Optional | Mandatory |

---

## Citation

```bibtex
@misc{rau2026stp,
  title        = {The Perfect Instruction: Empirical Validation of the
                  Triple-A Thesis through Actor-Agnostic Framework Design},
  author       = {Rau, Sebastian Johannes},
  year         = {2026},
  month        = {April},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19378044},
  url          = {https://doi.org/10.5281/zenodo.19378044},
  note         = {The Sealed Test Paradigm is introduced in this work
                  as AP2 (TestLock) + P4 (TDD) within Tb Meta OS Alpha}
}
```

---

## Author

**Sebastian Johannes Rau**  
Independent AI Research — Siegen/Wuppertal, Germany  
ORCID: [0009-0009-0801-6182](https://orcid.org/0009-0009-0801-6182)

*Built between September 2025 and April 2026 — from a basement, without funding, because the problem was real.*
