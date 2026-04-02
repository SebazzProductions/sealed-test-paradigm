"""
examples/basic_usage.py

End-to-end walkthrough of the Sealed Test Paradigm.
This example uses a trivial in-memory "agent" to show the mechanics.
Replace agent.generate() with any LLM call.
"""

from stp.core import BlueprintLayer, TestQueue, TestLock, GateCondition, TestSpec


# ── Step 1: Blueprint Layer (runs isolated from agent) ────────────────────────

print("── I. Blueprint Layer ─────────────────────────────")

blueprint = BlueprintLayer()
blueprint \
    .require(
        name        = "sanitize_input",
        description = "User input must be stripped of control characters",
        assertion   = "sanitize(input) contains no \\n or \\r",
        priority    = 0,
    ) \
    .require(
        name        = "token_limit",
        description = "Output must not exceed 512 tokens",
        assertion   = "len(output.split()) <= 512",
        priority    = 1,
    )

assert blueprint.validate(), "Blueprint must have specs before proceeding"
print(f"  Blueprint valid: {len(blueprint.specs())} required tests")


# ── Step 2: Test Queue ────────────────────────────────────────────────────────

print("\n── II. Test Queue ─────────────────────────────────")

queue = TestQueue()
for spec in blueprint.specs():
    queue.append(spec)

print(f"  Queued: {len(queue)} tests (append-only, ordered)")


# ── Step 3: TestLock ──────────────────────────────────────────────────────────

print("\n── III. TestLock ──────────────────────────────────")

lock    = TestLock()
sealed  = lock.seal_queue(queue)       # queue is now frozen

for s in sealed:
    verified = TestLock.verify(s)
    print(f"  [{s.spec.name}]  seal={s.seal[:16]}...  integrity={'OK' if verified else 'TAMPERED'}")

# Demonstrate tamper detection
import dataclasses, hashlib, json
tampered_spec = dataclasses.replace(sealed[0].spec, assertion="anything goes")
tampered_test = dataclasses.replace(sealed[0], spec=tampered_spec)
print(f"  Tamper check:   {'DETECTED ✓' if not TestLock.verify(tampered_test) else 'MISSED ✗'}")


# ── Step 4: Gate Condition ────────────────────────────────────────────────────

print("\n── IV. Gate Condition ─────────────────────────────")

# Simulate a test runner (replace with real test execution)
def test_runner(spec: TestSpec) -> bool:
    """Returns True if test passes. Initially everything fails (RED)."""
    results = {
        "sanitize_input": False,   # RED — agent must fix this
        "token_limit":    False,   # RED — agent must fix this
    }
    return results.get(spec.name, False)

gate = GateCondition(sealed).evaluate(test_runner)
report = gate.report()
print(f"  {report}")

if gate.red_exists():
    failing = gate.failing_specs()
    print(f"\n  Gate OPEN — agent may generate code for {len(failing)} failing test(s):")
    for spec in failing:
        print(f"    → {spec.name}: {spec.assertion}")
else:
    print("\n  Gate CLOSED — all tests green, nothing to write")


# ── Agent generates code, then we re-evaluate ─────────────────────────────────

print("\n── Agent generates code → re-evaluate ────────────")

def test_runner_after_fix(spec: TestSpec) -> bool:
    """Simulate agent having fixed the code."""
    return True   # both tests now pass

gate2 = GateCondition(sealed).evaluate(test_runner_after_fix)
report2 = gate2.report()
print(f"  {report2}")

if gate2.all_green():
    print("  ✓ All sealed tests GREEN. Paradigm complete.")
    print("  Agent produced: TDD-verified production code.")
