# Rerunner — Enterprise-Grade Master Engineering Plan
> **Mission**: Build the industry-standard deterministic flight recorder, replay engine, and CI test runner for AI agents and LLM applications.
> **Standard**: Production grade, zero-leak, strictly typed, benchmarked, and architected to attract contributions from elite AI engineers and frontier labs (Anthropic, OpenAI, Google DeepMind, LangChain).

---

## 1. Why Top MNCs & Frontier Labs Will Care (The Real Problem)

Frontier AI labs and enterprises spend millions of dollars running CI/CD pipelines and regression suites on AI agents.

### The Pain Point for Big Tech:
1. **Flaky CI Pipelines**: AI agent tests fail randomly because LLMs are non-deterministic, even with `temperature=0`.
2. **Massive Cloud API Bills**: Re-running test suites across thousands of PRs burns hundreds of thousands of dollars in LLM API credits.
3. **Impossibility of Debugging Step 8 in an 8-Step Agent**: If an agent fails on Step 8, engineers cannot reproduce the failure locally without re-running Steps 1–7.
4. **Dangerous Side-Effects in Tests**: Running an agent test risks firing real network calls, updating test DBs, or calling external APIs twice.

### How `rerunner` Solves This:
* **Cassette Record & Replay**: Intercepts `httpx` traffic (the engine inside Anthropic and OpenAI SDKs) and saves exact tokens/tool calls into an append-only, tamper-evident JSONL cassette.
* **$0 CI Replay**: All regression tests replay in **0 milliseconds** with **zero network calls** and **100% determinism**.
* **Fork-from-Step**: Replays Steps 1–7 from the cassette for free; runs Step 8 live against the model.
* **Side-Effect Safety Guard**: Intercepts `@tool(side_effect=True)` to prevent destructive external actions during replay.

---

## 2. Engineering Standards: The "MNC-Grade" Bar

To get senior engineers from top organizations to respect, star, and contribute to a repository, the project must adhere to strict software engineering standards:

```
+-------------------------------------------------------------------------+
|                         MNC ENGINEERING CRITERIA                        |
+------------------------------------+------------------------------------+
| 1. Pure Type Safety                | Strict mypy & pyright (0 `Any`).   |
| 2. Modern Python 3.11+ Standards   | PEP 621, hatchling, zero legacy    |
|                                    | setup.py, zero lockfile churn.    |
| 3. Extreme Linter Rigor            | Ruff (all rules enabled: E, F, I,  |
|                                    | UP, B, SIM, TCH, PTH, RUF).        |
| 4. Zero Hard Dependencies          | Core only requires httpx & pydantic|
| 5. Multi-OS Determinism            | 100% CI pass on Linux, macOS, Win. |
| 6. Architecture Decision Records   | Every major choice backed by an ADR|
+------------------------------------+------------------------------------+
```

---

## 3. High-Level System Architecture

```
                       +-----------------------------------+
                       |    User Agent Application / Test   |
                       | (Anthropic SDK, OpenAI SDK, etc.) |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------------------------+
                       |     rerunner.CassetteTransport    |
                       |  (Implements httpx.BaseTransport) |
                       +--------+-----------------+--------+
                                |                 |
         +----------------------+                 +----------------------+
         v                                                               v
+------------------+                                            +------------------+
| Normalizer &     |                                            |  Mode Controller |
| Tolerant Matcher |                                            |  (RECORD /       |
| (Strips volatile |                                            |   REPLAY /       |
|  IDs, timestamps)|                                            |   FORK)          |
+--------+---------+                                            +--------+---------+
         |                                                               |
         +----------------------+                 +----------------------+
                                |                 |
                                v                 v
                       +-----------------------------------+
                       |        Cassette Storage Engine    |
                       |    - Streaming JSONL storage      |
                       |    - SHA-256 Tamper-Evident Chain |
                       |    - Side-Effect Mock Interceptor |
                       +-----------------------------------+
```

---

## 4. Complete Repository Blueprint

```
rerunner/
├── pyproject.toml                 # Modern PEP 621 packaging (hatchling build)
├── LICENSE                        # Apache 2.0 (Permissive for enterprise use)
├── README.md                      # High-impact documentation with terminal demos
├── CONTRIBUTING.md                # World-class contribution guidelines
├── CODE_OF_CONDUCT.md             # Contributor Covenant v2.1
├── SECURITY.md                    # Enterprise vulnerability disclosure policy
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Matrix testing: Python 3.11, 3.12, 3.13 on Ubuntu, macOS, Windows
│   │   ├── lint.yml               # Ruff format + Ruff check + Mypy strict
│   │   └── release.yml            # Automated PyPI deployment on signed tags
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml         # Structured GitHub form
│   │   ├── feature_request.yml    # Structured feature proposal form
│   │   └── rfc.yml                # Request For Comments template
│   └── PULL_REQUEST_TEMPLATE.md   # Rigorous PR checklist
├── src/
│   └── rerunner/
│       ├── __init__.py            # Clean public API: record, replay, fork, step
│       ├── py.typed               # PEP 561 marker for complete typing support
│       ├── transport.py           # Synchronous CassetteTransport for httpx
│       ├── async_transport.py     # Asynchronous AsyncCassetteTransport
│       ├── matcher.py             # Tolerant request hasher & body normalizer
│       ├── cassette.py            # Append-only JSONL cassette storage engine
│       ├── models.py              # Pydantic v2 data models (Entry, Header, Request, Response)
│       ├── forker.py              # Fork-from-step execution controller
│       ├── side_effects.py        # @side_effect decorator and mock registry
│       ├── integrity.py           # Cryptographic SHA-256 hash chaining
│       ├── pytest_plugin.py       # Native pytest hook: @pytest.mark.rerunner
│       └── cli.py                 # Rich + Typer terminal interface
└── tests/
    ├── conftest.py                # Reusable test fixtures & local HTTP mock server
    ├── test_transport_sync.py     # Sync transport interception unit tests
    ├── test_transport_async.py    # Async transport interception unit tests
    ├── test_matcher.py            # Tolerant matching edge cases (volatile tokens)
    ├── test_streaming.py          # Server-Sent Events (SSE) streaming token replay
    ├── test_forker.py             # Fork-from-step state machine tests
    ├── test_side_effects.py       # Safe stubbing of external functions
    ├── test_integrity.py          # Tamper-evident hash chain verification
    ├── test_cli.py                # Command-line interface integration tests
    └── test_pytest_plugin.py      # Pytest fixture and marker integration tests
```

---

## 5. Phased Execution Roadmap

### Phase 1: Foundation & Packaging (Day 1–2)
* Setup `pyproject.toml` with strict typing (`mypy`), linting (`ruff`), and build system (`hatchling`).
* Define core immutable data structures in `models.py` using Pydantic v2.
* Implement append-only JSONL streaming parser in `cassette.py`.
* Implement SHA-256 tamper-evident hash chaining in `integrity.py`.

### Phase 2: HTTP Interception & Tolerant Matcher (Day 3–4)
* Implement `CassetteTransport` and `AsyncCassetteTransport` inheriting from `httpx.BaseTransport`.
* Build request normalizer:
  * Sort JSON keys deterministically.
  * Strip volatile HTTP headers (`User-Agent`, `x-request-id`, `Date`, dynamic session tokens).
* Handle Server-Sent Events (SSE) streaming chunks with zero data loss.

### Phase 3: Fork-from-Step & Side-Effect Engine (Day 5–6)
* Implement step counter and breakpoint logic in `forker.py`.
* Build `@tool(side_effect=True)` decorator in `side_effects.py` to record tool return values and prevent external mutation during replay.

### Phase 4: Developer Experience & Pytest Integration (Day 7–8)
* Implement Pytest plugin (`pytest_plugin.py`) providing `@pytest.mark.rerunner("cassette.jsonl")`.
* Implement CLI with Rich output:
  * `rerunner record <cassette> <cmd>`
  * `rerunner replay <cassette> <cmd>`
  * `rerunner fork <cassette> --step <N> <cmd>`
  * `rerunner verify <cassette>` (verifies cryptographic hash chain)
  * `rerunner diff <cassette_a> <cassette_b>` (highlights prompt/response divergence)

### Phase 5: Production Hardening & Open Source Launch (Day 9–10)
* 100% test coverage with automated GitHub Actions CI matrix (Ubuntu, macOS, Windows).
* Create real-world runnable examples with Anthropic Claude SDK and OpenAI SDK.
* Publish to PyPI and initiate outreach to AI engineering leaders.

---

## 6. How We Attract Frontier Lab & MNC Contributions

1. **Direct SDK Compatibility**:
   * Anthropic's Python SDK (`anthropic-python`) and OpenAI's Python SDK (`openai-python`) both accept a custom `http_client=httpx.Client(transport=rerunner.CassetteTransport(...))`.
   * Zero monkeypatching. It is clean, idiomatic, and works out-of-the-box.
2. **Issue Quality ("Good First Issue" & "Help Wanted")**:
   * Pre-write structured RFCs and issues for provider-specific edge cases (e.g., Gemini gRPC adapter, LangChain callback handler, LlamaIndex integration).
3. **Transparent Governance**:
   * Clear contribution workflow, fast automated CI checks, and respectful code review feedback.
