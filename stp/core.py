"""
stp/core.py — The Sealed Test Paradigm
Reference implementation of the four primitives.

DOI: 10.5281/zenodo.19378044
Author: Sebastian Johannes Rau, 2026
License: CC BY 4.0
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum


# ── Types ────────────────────────────────────────────────────────────────────

class TestStatus(Enum):
    PENDING  = "pending"   # not yet run
    RED      = "red"       # failing — agent may write code
    GREEN    = "green"     # passing — nothing to write
    LOCKED   = "locked"    # sealed, immutable


@dataclass(frozen=True)
class TestSpec:
    """Immutable test specification. Once created, identity is fixed."""
    name: str
    description: str
    assertion: str          # human-readable assertion string
    priority: int = 0       # lower = earlier in queue

    def to_dict(self) -> dict:
        return {
            "name":        self.name,
            "description": self.description,
            "assertion":   self.assertion,
            "priority":    self.priority,
        }


@dataclass(frozen=True)
class SealedTest:
    """A TestSpec after the TestLock has been applied.
    The executing agent may read this — but may never produce one itself."""
    spec:   TestSpec
    seal:   str             # SHA-256 of spec content
    status: TestStatus = TestStatus.LOCKED

    def evaluate(self, runner: Callable[[TestSpec], bool]) -> "SealedTest":
        """Run the test. Returns a new SealedTest with updated status.
        The seal is preserved — the spec cannot change."""
        passed = runner(self.spec)
        new_status = TestStatus.GREEN if passed else TestStatus.RED
        return SealedTest(spec=self.spec, seal=self.seal, status=new_status)

    @property
    def is_red(self) -> bool:
        return self.status == TestStatus.RED

    @property
    def is_green(self) -> bool:
        return self.status == TestStatus.GREEN


# ── Primitive I: Blueprint Layer ──────────────────────────────────────────────

class BlueprintLayer:
    """
    Defines which tests must exist before any agent execution.
    Must run in a context isolated from the executing agent.

    Invariant: No agent input influences which tests are required.
    """

    def __init__(self):
        self._specs: list[TestSpec] = []

    def require(
        self,
        name:        str,
        description: str = "",
        assertion:   str = "",
        priority:    int = 0,
    ) -> "BlueprintLayer":
        """Declare a required test. Returns self for chaining."""
        spec = TestSpec(
            name=name,
            description=description,
            assertion=assertion,
            priority=priority,
        )
        self._specs.append(spec)
        return self

    def specs(self) -> list[TestSpec]:
        """Return specs sorted by priority. Blueprint is now read-only."""
        return sorted(self._specs, key=lambda s: s.priority)

    def validate(self) -> bool:
        """Blueprint must have at least one spec before any execution."""
        return len(self._specs) > 0


# ── Primitive II: Test Queue ──────────────────────────────────────────────────

class TestQueue:
    """
    Ordered, append-only queue of test specifications.

    Invariant I₁ (partial): Tests exist in the queue before code generation.
    Invariant I₂ (partial): Append-only — no removal or modification.
    """

    def __init__(self):
        self._queue: list[TestSpec] = []
        self._sealed = False

    def append(self, spec: TestSpec) -> None:
        if self._sealed:
            raise RuntimeError(
                "TestQueue is sealed. No modifications permitted after lock."
            )
        self._queue.append(spec)

    def seal(self) -> None:
        """Prevent further appends. Called by TestLock before sealing."""
        self._sealed = True

    def __iter__(self):
        return iter(self._queue)

    def __len__(self):
        return len(self._queue)


# ── Primitive III: TestLock ───────────────────────────────────────────────────

class TestLock:
    """
    Seals every test in a queue with a cryptographic hash.
    After sealing, the queue is frozen and each test is individually tamper-evident.

    Invariant I₂: locked(t) → ¬modifiable(agent, t)
    """

    @staticmethod
    def _hash(spec: TestSpec) -> str:
        content = json.dumps(spec.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def seal_queue(self, queue: TestQueue) -> list[SealedTest]:
        """
        Seals the queue. Returns sealed tests.
        The queue is locked — no further appends possible.
        """
        queue.seal()
        return [
            SealedTest(spec=spec, seal=self._hash(spec))
            for spec in queue
        ]

    @staticmethod
    def verify(sealed: SealedTest) -> bool:
        """Verify a sealed test has not been tampered with."""
        expected = hashlib.sha256(
            json.dumps(sealed.spec.to_dict(), sort_keys=True).encode()
        ).hexdigest()
        return expected == sealed.seal


# ── Primitive IV: Gate Condition ──────────────────────────────────────────────

class GateCondition:
    """
    Controls access to code generation.
    The executing agent may only write code if a sealed, failing test exists.

    Invariant I₃: generate(c) iff ∃ t: locked(t) ∧ fails(t)
    """

    def __init__(self, sealed_tests: list[SealedTest]):
        self._tests = sealed_tests

    def evaluate(self, runner: Callable[[TestSpec], bool]) -> "GateCondition":
        """Run all sealed tests through the provided runner.
        Returns a new GateCondition with evaluated status."""
        evaluated = [t.evaluate(runner) for t in self._tests]
        return GateCondition(evaluated)

    def red_exists(self) -> bool:
        """I₃: Is there at least one failing sealed test?"""
        return any(t.is_red for t in self._tests)

    def failing_specs(self) -> list[TestSpec]:
        """Return specs the agent is permitted to address."""
        return [t.spec for t in self._tests if t.is_red]

    def all_green(self) -> bool:
        """All tests pass — nothing for the agent to write."""
        return all(t.is_green for t in self._tests)

    def report(self) -> dict:
        return {
            "total":         len(self._tests),
            "red":           sum(1 for t in self._tests if t.is_red),
            "green":         sum(1 for t in self._tests if t.is_green),
            "pending":       sum(1 for t in self._tests if t.status == TestStatus.PENDING),
            "gate_open":     self.red_exists(),
        }
