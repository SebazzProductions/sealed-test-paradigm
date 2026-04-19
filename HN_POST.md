# Show HN Post — Sealed Test Paradigm

*Ready-to-use draft. Post during Tue/Wed/Thu 08:00–10:00 EST (14:00–16:00 CEST).*

---

## HN Post Title

```
Show HN: Sealed Test Paradigm – preventing AI agents from modifying their own tests
```

*80 chars — under HN's title limit. Concrete problem + concrete mechanism.*

---

## Post Body (first comment)

```
Hi HN,

Solo-developer from Siegen. Been working on agent frameworks for a
while, and one structural failure kept breaking me: agents "passing"
tests by writing them after the code, or quietly adjusting tests
until they pass. Standard TDD relies on human discipline — which
falls apart when the executor can rewrite the spec.

STP makes test modification structurally impossible. Four primitives:

1. Blueprint Layer — isolated test planning, agent has no access
2. Test Queue — append-only, ordered, no deletions
3. TestLock — SHA-256 seal; agent gets spec + hash, never writable source
4. Gate Condition — code generation only when a sealed test actively fails

Three formal invariants:

  I₁ Temporal:    ∀ t,c: commit(t) < generate(c)
  I₂ Structural:  ∀ t in queue: locked(t) → ¬modifiable(agent, t)
  I₃ Behavioral:  generate(c) iff ∃ t: locked(t) ∧ fails(t)

Implementation-agnostic — enforce via Git hooks, CI, an orchestration
layer, or the ~120-line Python reference. Works with AutoGen,
LangChain, CrewAI, Claude tool-use, local LLMs — it's a wrapper-level
primitive, not a framework.

Empirical validation: tested across 9 LLM actors (Claude, Codex,
DeepSeek, Perplexity, Gemini, Nemotron, and others) — score
variance under 15 points on benchmark consistency, confirming actor
exchangeability. My TypeScript production implementation (Omega
Engine) sits at 163/163 tests passing with zero manual intervention.

Licensed CC BY 4.0. Full paper with formal proofs is on Zenodo.

Repo:  https://github.com/SebazzProductions/sealed-test-paradigm
Paper: https://doi.org/10.5281/zenodo.19378044

Genuinely open question I haven't solved: the Blueprint Layer itself
has no formal sufficiency guarantee. STP structurally enforces that
agents can't cheat sealed tests, but doesn't prove the blueprint
captured everything that mattered. That feels like the next primitive
I haven't found yet. Would love input.

Built in a basement between September 2025 and April 2026. Unfunded.
The problem was real enough that the solution had to exist before I
could ship what depended on it.
```

---

## Why This Draft (design notes)

- **Title**: 80 chars, concrete problem + mechanism. No DOI in title (too academic for HN).
- **Opener**: leads with the problem after a brief personal anchor. HN prefers problem-first.
- **Invariants in math notation**: signals rigor, HN engineering crowd respects this.
- **Framework names (AutoGen/LangChain/CrewAI)**: concrete reference points, domain awareness.
- **"9 LLM actors" + "163/163 tests"**: empirical credibility anchors.
- **Explicit open question at end**: intellectual honesty. HN values this highly.
- **"Built in basement, unfunded"**: founder-voice without sob-story framing.
- **No mention of Alessja**: launch card preserved for later.
- **No "revolutionary/groundbreaking/consciousness"**: hype claims get killed fast on HN.

---

## Preparation Checklist Before Posting

- [x] LICENSE file (CC BY 4.0) present in repo
- [ ] 5–10 GitHub stars from trusted contacts (prevents "abandoned-looking" first impression)
- [ ] Test suite runs cleanly on fresh clone (`pytest tests/` from repo root)
- [ ] README DOI badge renders correctly
- [ ] First comment-body copy-pasted, reviewed once more before submit

---

## Post-Posting Response Strategy

**If asked "why not just use git for test locking"**:
Valid lightweight enforcement of I₂ — git commit hash serves as seal.
STP is framework-agnostic about mechanism. Git hooks are a valid
implementation; you'd just need Blueprint Layer isolation and Gate
Condition separately.

**If asked "how does this differ from frozen test contracts in normal TDD"**:
Normal TDD assumes human discipline. STP removes the ability to modify
at the architectural level — not a policy, a structural constraint.

**If asked about Blueprint sufficiency**:
Acknowledge openly — that's the honest open question. Structural
enforcement is solid, formal verification that the blueprint captured
all necessary tests is not. That's where I'm most uncertain.

**If asked about the larger framework**:
Mention briefly that STP is extracted from Tb Meta OS Alpha (link DOI),
but don't pivot the thread. Keep focus on STP itself. The companion
app that depends on it will be a separate post in 2-3 weeks.

**If dismissed ("it's just TDD")**:
Agree-and-differ: yes, it's TDD — but TDD for actors who can rewrite
the rules. That's the novel constraint, and it requires architectural
enforcement rather than discipline.

---

## Topics to Mention in Body-Comments if Asked

- Implementation-agnostic (not Python-locked; works with any language/framework)
- Validated empirically across 9 different LLM actors
- ~120 lines of reference Python, no dependencies beyond stdlib
- Formal invariants are machine-verifiable (tests in repo)
- Extracted as a standalone primitive from a larger framework

---

## Timing

- **Best window**: Tuesday/Wednesday/Thursday 08:00–10:00 EST (14:00–16:00 CEST)
- **Avoid**: Monday mornings (weekend backlog), Friday afternoons (checked out)
- **Current draft time**: 2026-04-19 23:30 CEST — hold post for Tuesday morning (14:00 CEST)
