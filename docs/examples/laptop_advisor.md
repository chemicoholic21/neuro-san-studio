# Laptop Advisor — Grounded Multi-Agent Network

A right-sized submission for the **Grounded Agent Network** assignment: a
multi-agent network in neuro-san that answers domain questions by coordinating
specialists and grounding every fact in deterministic, local coded-tool data.

## Use case

Help a user choose a laptop. This is a good multi-agent case because a single
agent would have to juggle three unrelated concerns at once:

1. **Hard filtering** — budget, RAM, weight, OS, use case (objective, numeric).
2. **Review synthesis** — rating, reliability, pros/cons (subjective quality).
3. **Policy** — warranty, return window, support (rules that can flip a decision).

Splitting these keeps each agent's boundary crisp and each answer traceable.

## Architecture

```
User
 │
 ▼
LaptopAdvisor  (front man / orchestrator — no knowledge of its own)
 ├── SpecScout      → LaptopSpecsTool    (filters local catalog CSV)
 ├── ReviewAnalyst  → LaptopReviewsTool  (reads local reviews JSON)
 └── PolicyAuditor  → LaptopPolicyTool   (reads local policies JSON)
```

- **Agent boundaries:** one specialist per data source / concern; the front man
  only orchestrates and compiles evidence.
- **Grounding:** each specialist is *required* to call its coded tool and forbidden
  from using model knowledge. Coded tools read only local files
  (`coded_tools/laptop_advisor/data/`). Unknown items fail closed (return `None`
  / an `error`) so the model says "not in the data" instead of hallucinating.
- **Coded tools:** thin `CodedTool` adapters over a pure data layer
  (`laptop_data.py`) that has no LLM/neuro-san dependency — so the grounding logic
  is unit-testable on its own.
- **Decision with evidence:** the front man ends with a single recommendation (or
  a short ranked list) justified by the specs, rating and policy it actually
  retrieved.

## Files

| Path | Role |
|---|---|
| `registries/laptop_advisor/laptop_advisor.hocon` | Agent network definition |
| `registries/laptop_advisor/manifest.hocon` | Group manifest (included by top-level manifest) |
| `coded_tools/laptop_advisor/laptop_data.py` | Deterministic data layer (no LLM dep) |
| `coded_tools/laptop_advisor/laptop_specs_tool.py` | Spec/price filter tool |
| `coded_tools/laptop_advisor/laptop_reviews_tool.py` | Review/reliability tool |
| `coded_tools/laptop_advisor/laptop_policy_tool.py` | Warranty/return/support tool |
| `coded_tools/laptop_advisor/data/*.{csv,json}` | Local ground-truth datasets |
| `tests/laptop_advisor/validate_grounding.py` | Deterministic validation (no key needed) |

## Validate the grounding (no API key required)

```bash
PYTHONPATH=. python3 tests/laptop_advisor/validate_grounding.py
```

Checks referential integrity across the datasets, that filters never violate
their constraints, that lookups resolve by id and name, that facts are returned
verbatim, and that unknown items fail closed.

## Run the full network

```bash
pip install -r requirements.txt          # installs neuro-san
# pick an LLM provider — e.g. Mistral for this assignment:
pip install langchain-mistralai==1.1.2
export MISTRAL_API_KEY="..."              # or set config/llm_config.hocon
python -m neuro_san_studio run
# open http://localhost:4173/ and choose "LaptopAdvisor"
```

Try the sample queries in the HOCON `metadata.sample_queries`, e.g.
*"I have $1000 for a light laptop for programming. What do you recommend?"*

## Deliberately out of scope (avoiding over-engineering)

No web search, no writing/executing anything, no retry/iteration loops, no
external services. The assignment grades **agent boundaries, grounding, coded
tools, and validation** — this network targets exactly those and nothing more.
