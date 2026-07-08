# Project Notes

## Current: Laptop Advisor (assignment submission)

A right-sized **grounded multi-agent network** for the "Grounded Agent Network"
assignment. See [`docs/examples/laptop_advisor.md`](examples/laptop_advisor.md).
Scope is deliberately limited to the four grading criteria — agent boundaries,
grounding, coded tools, validation — and nothing more.

---

## Separate future project (NOT this assignment)

### Production-Grade Agentic Issue Resolver (AAOSA)

An autonomous **GitHub issue resolver** built on neuro-san — inspired by, but
kept entirely separate from, the assignment above. It is **not** an extension or
over-engineering of the Laptop Advisor; it is its own project to be built later.

High-level design (already sketched):

- **Orchestrator** fetches a GitHub issue, then delegates to specialists.
- **Issue Triage** agent extracts metadata + reproduction steps.
- **Code Investigation** + **Research** agents (parallel) gather grounded evidence.
- **Patch & PR** agent generates a minimal diff and opens a *draft* PR.
- **Validation** agent runs tests/lint/type-check as the deterministic pass/fail gate.
- Safety rails: sandboxed file writes enforced in code, max-iteration cap,
  confirmed before/after reproduction, and a first-class **NO-FIX / NEEDS-HUMAN**
  outcome.

Why it is separate: it *mutates code* and touches external systems (git, PRs,
web), which is a fundamentally different and riskier problem than grounded Q&A.
Building it deserves its own repo/branch and its own scope, not a bolt-on here.

**Recommended first step when we build it:** a thin vertical slice scoped to
"make a failing test pass" on a real repo clone, run against ~3 real issues to
get reality-based feedback before broadening.
