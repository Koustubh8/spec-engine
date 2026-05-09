---
name: software-spec-graph
description: Build software from specification graphs. Spec-driven development where the knowledge graph IS the spec — queryable, lintable, and directly translatable to code. Adapted from OpenSpec's delta-based approach but graph-native.
version: 1.5.0
---

# Software Specification Graph

A graph-native adaptation of OpenSpec's spec-driven development methodology. Instead of markdown files in a folder hierarchy, specifications live as nodes with typed edges in the knowledge graph — making them queryable, lintable, and directly translatable to code by an AI agent.

## When to Use This Skill

- Building a new feature with structured requirements
- Making changes to an existing system (brownfield)
- Running impact analysis: "what breaks if I change X?"
- Verifying completeness: "does every endpoint have error handling?"
- Generating code from a specification graph
- Coordinating multi-component changes

## Architecture

The spec graph has four layers:

```
LAYER 1: SPECS (source of truth)
  spec nodes → contain requirements → each requirement has scenarios
  "What the system does"

LAYER 2: CHANGES (proposed modifications)
  change nodes → add/modify/remove requirements
  Deltas relative to current specs
  "What we're about to change"

LAYER 3: DESIGN (technical decisions)
  design nodes → reference → tools, patterns, architecture
  "How we're building it"

LAYER 4: VERIFICATION (correctness)
  test nodes → verify → requirements, scenarios
  implementation nodes → implement → specs
  "Proof it works"
```

## Node Kinds

| Kind | Purpose | Example |
|------|---------|---------|
| `spec` | Behavior contract for a component | `auth-spec` describes what auth-module does |
| `requirement` | A specific behavior (SHALL/MUST/SHOULD) | `user-auth` — system SHALL issue JWT on login |
| `scenario` | Given-When-Then example | `valid-login` — Given valid creds, When submit, Then JWT |
| `change` | Proposed modification (delta) | `add-2fa` — adds 2FA requirement to auth-spec |
| `design` | Technical approach document | `2fa-design` — TOTP via speakeasy, QR enrollment |
| `task` | Implementation checklist item | `1.1-create-totp-service` |

## The 17 Spec Predicates

### Contract predicates (define interfaces)

| Predicate | Direction | Usage |
|-----------|-----------|-------|
| `exposes` | spec → endpoint | `auth-spec exposes POST /auth/login` |
| `accepts` | endpoint → schema | `POST /auth/login accepts LoginPayload` |
| `returns` | endpoint → schema | `GET /users returns User[]` |
| `triggers` | event → action | `payment_success triggers invoice_generation` |
| `fails_with` | condition → error | `invalid_token fails_with HTTP_401` |

### Spec structure predicates

| Predicate | Direction | Usage |
|-----------|-----------|-------|
| `spec_of` | spec → component | `auth-spec spec_of auth-module` |
| `contains` | spec → spec OR spec → requirement | `platform-spec contains data-model-spec` — links a top-level spec to its sub-specs or to individual requirements. Supports hierarchical decomposition. Queryable: `query.py "platform-spec" --via contains --depth 3` returns the full spec tree. |
| `portion_of` | node → container | `polymorphic-nodes portion_of data-model-spec` — inverse of contains, auto-created by ingest |
| `scenario_for` | scenario → requirement | `valid-login scenario_for user-auth` |

### Change/delta predicates

| Predicate | Direction | Usage |
|-----------|-----------|-------|
| `change_for` | change → spec | `add-2fa change_for auth-spec` |
| `adds` | change → requirement | `add-2fa adds 2fa-requirement` |
| `modifies` | change → requirement | `add-2fa modifies session-expiry` |
| `removes` | change → requirement | `add-2fa removes remember-me` |
| `archives_to` | change → spec | `add-2fa archives_to auth-spec` |

### File and deployment predicates

| Predicate | Direction | Usage |
|-----------|-----------|-------|
| `touches` | task → file | `task-dm-css touches frontend/index.html` — which file this task modifies |
| `deploys_to` | component → target | `scraper-runner deploys_to k8s-cluster` — where this component runs |
| `authenticates_via` | component → method | `scraper-api authenticates_via jwt-token` — how this component authenticates |
| `shares_schema_with` | comp ↔ comp | `main-api shares_schema_with prefect-flow` — shared DB schema (symmetric) |

`touches` enables forward queries ("which files change for this requirement?") and reverse queries ("which requirements affect this file?"). `deploys_to` + `authenticates_via` enable lint rules that catch missing deployment/auth specs before implementation. `shares_schema_with` enables schema consistency checks across components that share a database.

### Verification predicates

| Predicate | Direction | Usage |
|-----------|-----------|-------|
| `tests` | test → requirement | `test-login-flow tests user-auth` |
| `guarantees` | component → property | `idempotency_key guarantees exactly_once` |
| `implements` | code → spec | `AuthController implements auth-spec` |
| `conforms_to` | artifact → standard | `auth-spec conforms_to RFC_6749` |

### Reuse predicate

| Predicate | Direction | Usage |
|-----------|-----------|-------|
| `reuses` | project → pattern | `candle-crm-v2 reuses ig-handle-as-primary-key` — links a built project to the reusable patterns it leverages. Enables inventory queries: "which projects use this pattern?" |

## Workflow

The full OpenSpec-adapted lifecycle. Do NOT skip Phases 0-3 — exploration before specification is where the value lives. Jumping straight to specs produces code that fits the words but misses the constraints.

### Phase 0: Requirement Intake

A single line of requirement arrives. Example: "no code platform for instagram scraping using scrapy as a backend, keep ui/ux minimalistic"

Do NOT immediately write specs. This is raw material for exploration.

**CRITICAL: Involve the user before building anything.** The exploration phase is not a solo activity. Use `clarify` tool calls to ask the user 5-7 probing questions about their workflow, pain points, volume, constraints, and existing tools. Every answer becomes a concept node in the exploration graph with a `constrains` edge. What you discover will fundamentally change the design — as it did when "CRM for candle influencer" revealed DM-based ordering and UPI screenshot verification that the initial build completely missed.

**Use multiple-choice clarifies for rapid constraint discovery.** Offering `choices_offered` narrows down domains much faster than open-ended questions. The pattern is: start broad (genre/framework/domain), then scope (project size/complexity), then aesthetic/style.

**Example rapid clarification workflow** (from a game project — took 3 rounds to go from "build a game" to a fully scoped spec):

```
Round 1 (genre):
  clarify(question="What genre?",
    choices=["Top-down exploration", "Puzzle", "Action/arcade", "Strategy"])
  → Action/arcade

Round 2 (sub-genre):
  clarify(question="Which sub-genre?",
    choices=["Side-scrolling shooter", "Vertical shoot-em-up", "Precision platformer", "Run-n-gun"])
  → Side-scrolling shooter

Round 3 (visual style + scope):
  clarify(question="Visual style?",
    choices=["Pixel art", "Geometric", "ASCII"])
  → ASCII (terminal aesthetic)
  
  clarify(question="Scope?",
    choices=["Single level + boss", "3-5 levels", "Procedural"])
  → Single level + boss

Result after 3 rounds: "ASCII Contra-style side-scrolling shooter, 1 level + boss"
→ Ingested as sub-problems: player-system, enemy-system, level-scrolling, weapons, boss, HUD, rendering
```

**Example open-ended workflow for business/CRM apps:**

```
1. clarify: "How do orders come in? Pick the most common channel."
   → Answer ingested as: dm-order-channel constrains customer-mgmt

2. clarify: "What's the #1 pain point?"
   → Answer ingested as: core-pain-buried-dms constrains order-tracking

3. clarify: "How many products / how often does catalog change?"
   → Answer ingested as: catalog-10-plus constrains inventory-mgmt

4. clarify: "Roughly how many orders per day?"
   → Answer ingested as: volume-20-50 constrains order-tracking

5. clarify: "How do customers pay?"
   → Answer ingested as: payment-upi-screenshot constrains payment-tracking

6. clarify: "How do you deliver?"
   → Answer ingested as: delivery-dunzo-porter constrains order-tracking
```

**Rule of thumb:** If the domain is creative/entertainment (game, art, UI), use multiple-choice for rapid constraint gathering. If the domain is business/operations (CRM, analytics, e-commerce), use open-ended questions to surface unknown workflows. Both approaches immediately ingest answers into the graph.

Each answer is immediately ingested into the knowledge graph so the exploration is queryable forever. The resulting design is shaped by real constraints, not assumptions. This is the single highest-leverage step in the entire lifecycle.

### Phase 0.5: GRAPH INVENTORY — Query Reusable Assets (NEW — May 2026)

**CRITICAL: Before proposing ANY new spec, query what already exists.** The exploration phase is not greenfield. Query the knowledge graph for reusable patterns, existing specs, and working implementations that can be adapted.

```bash
# What reusable patterns exist?
python3 scripts/query.py "reusable-pattern" --depth 1

# What specs are already implemented?
# Look for specs with implements edges from code nodes

# What tools/stack do we already use?
python3 scripts/query.py "koustubh" --depth 1 --via uses,builds
```

The agent MUST present the reusable inventory to the user before creating new specs. Every new spec should have `reuses` edges to the patterns it leverages.

**Lint enforcement:** `GRAPH_INVENTORY_CHECK` — warns if a new change has no `reuses` edges to existing `reusable-pattern` nodes. `REUSE_CHECK` — warns if exploration didn't query reusable-pattern before proposing.

### Phase 1: PROPOSE — Decompose and Explore

Create an exploration change node. This captures the discovery process before any spec exists.

```bash
python3 scripts/ingest.py explore-<project> change_for <platform-spec> \
  --subject-kind changes --object-kind specs
```

**Decomposition:** Break the requirement into sub-problems. Each becomes a concept node with an `adds` edge. The decomposition should reveal: distinct concerns, dependencies, and what the user is really asking for.

```bash
python3 scripts/ingest.py explore-ig-scraper adds no-code-builder \
  --subject-kind changes --object-kind concepts
# ... one per decomposed concern (typically 5-10)
```

### Phase 2: EXPLORE — Analyze Constraints, Risks, Unknowns

For each sub-problem, identify **constraints** (hard limits), **risks** (things that might fail), **unknowns** (things to learn), and **trade-offs** (competing forces). Each becomes a concept node with a `constrains` edge to the affected sub-problem.

```bash
python3 scripts/ingest.py ig-anti-bot-concern constrains ig-data-extraction \
  --subject-kind concepts --object-kind concepts
```

**Lint check:** Every sub-problem should have at least one `constrains` edge. A sub-problem with no constraints hasn't been explored.

### Phase 3: DECIDE — Architecture Options with Rationale

Enumerate architecture options. Mark chosen vs rejected with explicit rationale edges. Use the `supersedes` + `blocks` + `enables` triad to capture WHY:

```bash
# Options
python3 scripts/ingest.py explore-ig-scraper adds option-scrapy-prefect \
  --subject-kind changes --object-kind concepts

# Chosen supersedes rejected
python3 scripts/ingest.py option-scrapy-prefect supersedes option-selenium-celery \
  --subject-kind concepts --object-kind concepts

# Rationale: rejected option blocks a core requirement
python3 scripts/ingest.py option-selenium-celery blocks no-code-builder \
  --subject-kind concepts --object-kind concepts

# Chosen option enables the platform
python3 scripts/ingest.py option-scrapy-prefect enables ig-scraper-platform \
  --subject-kind concepts --object-kind specs
```

Future agents reading the graph won't just see "use Scrapy" — they'll see what was rejected and why.

### Phase 4: SPECIFY — Requirements and Scenarios
    │     ├── guarantees → totp_based_mfa
    │     ├── scenario_for → scen/2fa-enrollment
    │     │     (GIVEN user without 2FA, WHEN they enable, THEN QR displayed)
    │     └── scenario_for → scen/2fa-login
    │           (GIVEN user with 2FA, WHEN valid creds, THEN OTP challenge)
    ├── modifies → req/session-expiry
    │     └── (30min → 15min)
    └── removes → req/remember-me
```

**Commands:**
```bash
# Create a change node (use plural kinds — see knowledge-graph gotcha #8)
python3 scripts/ingest.py add-2fa change_for auth-spec --subject-kind changess --object-kind specss

# Add requirements it introduces
python3 scripts/ingest.py add-2fa adds 2fa-requirement --subject-kind changess --object-kind requirementss --tags "security,mfa"

# Add scenarios
python3 scripts/ingest.py 2fa-enrollment scenario_for 2fa-requirement --subject-kind scenarios --object-kind requirementss
```

### Phase 5: Lint — Verify Completeness (10 rules)

Run ALL 10 rules before implementation. The rules were built from real failures — each one prevents a class of bug we've already hit:

```bash
python3 scripts/spec-lint.py  # runs all 10
```

| Rule | Severity | What it catches | Learned from |
|------|----------|-----------------|--------------|
| EXPOSES_HAS_CONTRACT | ERROR | Exposed endpoint has no accepts/returns | Missing API contracts |
| SCENARIO_FOR_REQ | WARNING | Requirement has no Given-When-Then scenario | Untestable requirements |
| GUARANTEES_HAS_TESTS | ERROR | Guaranteed property has no test verifying it | Untested guarantees |
| NO_ORPHAN_REQUIREMENTS | WARNING | Requirement not contained in any spec | Floating requirements |
| TRIGGERS_HAS_CONSUMER | WARNING | Event trigger has no handler consuming it | Orphaned events |
| SCHEMA_CONSISTENCY | ERROR | Components sharing DB have different schemas | IG Scraper review: Prefect vs main.py schema mismatch |
| DEPLOYMENT_SPECIFIED | WARNING | Exposed spec has no deploys_to edge | Prefect flows not deployed |
| AUTH_SPECIFIED | WARNING | Exposed endpoint has no authenticates_via | No auth on any IG Scraper endpoint |
| CONSISTENT_FALLBACKS | WARNING | Sibling specs use different error handling | Profile spider had fallback, hashtag didn't |
| ASYNC_LONG_RUNNING | ERROR | Job-executing spec has no async backend | Sync subprocess blocking API for 5 min |
| EXPLORATION_GATE | ERROR | Archived change has no findings | Agent forgot to ingest clarify responses into graph |
| GRAPH_UPDATE_CHECKPOINT | WARNING | Exploration-tagged change has zero findings | Agent skipped graph updates during exploration |
| GRAPH_INVENTORY_CHECK | WARNING | New spec has no `reuses` edges | Didn't query reusable-pattern before building |
| REUSE_CHECK | WARNING | Exploration didn't reference existing patterns | Missing inventory step before proposing specs |

When a lint rule fires, treat it as a spec gap — add the missing edge/node, don't just note it.

### Phase 5b: Production Readiness Lint (12 rules)

After the spec-lint passes, run the production readiness linter to catch operational gaps that won't be visible until deployment:

```bash
python3 tools/spec-studio/backend/prod_lint.py   # or via API: GET /api/lint/prod
```

| # | Rule | Severity | What it checks |
|---|------|----------|---------------|
| P1 | LOGGING_SPECIFIED | Warning | Every endpoint has logging framework reference |
| P2 | ERROR_HANDLING_SPECIFIED | Error | Every `fails_with` condition has an error handler spec |
| P3 | INPUT_VALIDATION_SPECIFIED | Warning | Every `accepts` endpoint has a schema/Pydantic reference |
| P4 | HEALTH_ENDPOINT_SPECIFIED | Warning | Service has `GET /health` or `GET /readyz` |
| P5 | CORS_CONFIGURED | Warning | API spec references CORS or allowed origins |
| P6 | TIMEOUT_SPECIFIED | Warning | Long-running operations have timeout specs |
| P7 | RETRY_SPECIFIED | Warning | External service calls have retry strategy |
| P8 | CONFIG_EXTERNALIZED | Warning | Configuration uses env vars, not hardcoding |
| P9 | MIGRATION_STRATEGY | Warning | DB schema changes reference Alembic or migration tool |
| P10 | ENVIRONMENTS_DEFINED | Warning | Spec has `deploys_to` for staging/prod targets |
| P11 | MONITORING_SPECIFIED | Warning | Service references monitoring/metrics (Prometheus, Grafana) |
| P12 | CI_CONFIGURED | Warning | Project references CI pipeline (GitHub Actions, etc.) |

**Scoring:** 12/12 🟢 Production ready | 10-11 🟡 Minor gaps, ship with tracking | 7-9 🟠 Needs work before production | 0-6 🔴 Not production ready, DO NOT DEPLOY

Each rule queries the spec graph for specific edge/node patterns. Rules are implemented in `tools/spec-studio/backend/prod_lint.py` and follow a standard pattern: query the DB for relevant nodes/edges → return (passed: bool, message: str). See `references/prod-readiness-linter-guide.md` for rule implementations.

Addressing production lint gaps often means adding new spec nodes (health endpoint spec, CORS config, timeout requirements) — treat it as spec expansion, not busywork.

### Phase 6: Impact Analysis

Before implementing, understand blast radius:

```bash
# What depends on what I'm changing?
python3 scripts/query.py "auth-spec" --depth 3 --via depends_on,triggers,implements

# What endpoints does this spec expose?
python3 scripts/query.py "auth-spec" --via exposes --depth 2

# Trace a requirement to all tests
python3 scripts/query.py --path "user-auth" "test-login-flow"
```

### Phase 7: Implement

The agent reads the subgraph and generates code:

```
For each requirement in spec:
  For each scenario:
    Generate test from Given-When-Then
  Generate implementation
    - exposed endpoints → route handlers (from `exposes` edges)
    - input validation → from `accepts` schema edges
    - error responses → from `fails_with` edges
    - event publishing → from `triggers` edges
```

### Phase 8: Archive

```bash
# Mark change as archived (merged into spec)
python3 scripts/ingest.py add-2fa archives_to auth-spec --subject-kind changes --object-kind specs

# The supersedes edge preserves the history forever
# auth-spec superseded_by add-2fa  (reverse edge, auto-created)
```

The `superseded_by` edge is permanent. You can always trace: "Why does auth-spec have 2FA?" → follows the edge back to the change.

## The Archive Edge Chain

```
auth-spec (v3) ←──superseded_by── add-2fa (change)
    │                                    │
auth-spec (v2) ←──superseded_by── add-oauth (change)
    │                                    │
auth-spec (v1) ←──superseded_by── initial-auth (change)
```

Every version is traceable. Every change is accountable. This is what OpenSpec loses on archive and what our graph preserves.

## Query Patterns

### Impact analysis
"Show me everything that depends on the User model"
```bash
python3 scripts/query.py "user-model" --depth 5 --via exposes,accepts,returns,depends_on,triggers,implements
```

### File traceability
"Which files need to change for this requirement?"
```bash
# Forward: requirement → task → file
python3 scripts/query.py "dark-mode-requirement" --depth 3 --via adds,touches
```
```cypher
-- NebulaGraph Cypher version
MATCH (req:requirement)<-[:adds]-(ch:delta)-[:adds]->(t:task)-[:touches]->(f)
WHERE id(req)=="requirements/dark-mode-requirement"
RETURN req, ch, t, f
```

"Which requirements affect this file?"
```cypher
-- Reverse: file → task → requirement
MATCH (f)<-[:touches]-(t:task)<-[:adds]-(ch:delta)-[:adds]->(req)
WHERE id(f)=="references/frontend-index-html"
RETURN f, t, ch, req
```

### Contract completeness
"Does the payments spec have all required contracts?"
```bash
python3 scripts/query.py "payments-spec" --via exposes --depth 1
# Then for each endpoint, check: has accepts? has returns? has fails_with?
```

### Change history
"Show me every change to auth-spec, in order"
```bash
python3 scripts/query.py "auth-spec" --via superseded_by --depth 5
# Follows the superseded_by chain back through all archived changes
```

### Test coverage
"How well is auth-spec tested?"
```bash
python3 scripts/query.py "auth-spec" --depth 3 --via tests,scenario_for
# Shows requirements → scenarios → tests
```

## Templates

### Spec node template

```markdown
---
title: Auth Specification
kind: spec
created: 2026-05-08
updated: 2026-05-08
tags: [security, auth, api]
---

# Auth Specification

Authentication and session management for the application.

## Purpose
Issue and validate JWT tokens for user authentication. Support credential-based login with optional MFA.

## Non-Goals
- OAuth2 social login (separate spec)
- Role-based access control (separate spec)

|rel:spec_of| [[tools/auth-module]]
|rel:conforms_to| [[references/RFC_7519]]
|rel:contains| [[requirements/user-auth]]
|rel:contains| [[requirements/session-expiry]]
```

### Requirement node template

```markdown
---
title: User Authentication
kind: requirement
created: 2026-05-08
updated: 2026-05-08
tags: [auth, login, jwt]
strength: SHALL
---

# User Authentication

The system SHALL issue a JWT token upon successful credential verification.

|rel:portion_of| [[specs/auth-spec]]
|rel:guarantees| [[concepts/secure_credential_storage]]
```

### Scenario node template

```markdown
---
title: Valid Login
kind: scenario
created: 2026-05-08
updated: 2026-05-08
tags: [auth, happy-path]
---

# Valid Login

**GIVEN** a user with valid email and password
**WHEN** the user submits the login form
**THEN** a JWT token is returned with 15-minute expiry
**AND** the user is redirected to the dashboard

|rel:scenario_for| [[requirements/user-auth]]
```

### Change node template

```markdown
---
title: Add Two-Factor Authentication
kind: change
created: 2026-05-08
updated: 2026-05-08
tags: [auth, security, mfa]
status: proposed
---

# Add Two-Factor Authentication

## Intent
Add TOTP-based two-factor authentication to strengthen login security.

## Scope
In: TOTP enrollment, OTP challenge during login, recovery codes
Out: SMS-based 2FA, hardware keys (future)

|rel:change_for| [[specs/auth-spec]]
|rel:adds| [[requirements/2fa-requirement]]
|rel:modifies| [[requirements/session-expiry]]
|rel:removes| [[requirements/remember-me]]
```

## NebulaGraph Backend

The spec graph can be synced to NebulaGraph for Cypher queries, visualization, and code generation. See the `knowledge-graph` skill's `references/nebulagraph-integration.md` for full setup. Quick summary:

```bash
# After NebulaGraph is running (docker compose up):
python3 ~/mywork/nebula/sync_markdown_to_nebula.py     # sync specs
python3 ~/.hermes/skills/software-development/software-spec-graph/scripts/spec-lint.py  # verify
python3 ~/mywork/nebula/gen_fastapi.py specs/auth-spec  # generate code
```

**NebulaGraph Studio (visualization):** http://localhost:7001 — connect with host `graphd:9669`, user `root`, password `nebula`, select space `knowledge_graph`.

**Sample Cypher query for Studio:**
```cypher
MATCH p=(:spec)-[*1..2]->(:spec) 
WHERE id(startNode(p))=="specs/ig-scraper-platform" 
RETURN p
```

## Pitfalls

- **META: Update the graph after EVERY critical phase.** The agent has repeatedly forgotten to ingest findings after clarify responses, exploration, code review, and build completions. This is now enforced by EXPLORATION_GATE and GRAPH_UPDATE_CHECKPOINT lint rules. After every clarify response: immediately ingest the finding. After every exploration: link findings to sub-problems. After every code review: link issues to specs. The graph must reflect current state at all times — it is the source of truth, not an afterthought.
- **Don't skip the exploration phase** — a single-line requirement like "no code platform for instagram scraping" needs decomposition BEFORE specs. Without exploration, you'll write specs that fit the words but miss the constraints (e.g., Instagram anti-bot blocking, no-code vs Scrapy complexity trade-off). The exploration graph (Phases 0-3) captures WHY decisions were made. Future agents reading the graph deserve that context.
- **Don't put implementation in specs** — specs are WHAT, design is HOW. If you find yourself writing "use React Context" in a spec, move it to a design node.
- **Every requirement needs at least one scenario** — a requirement without a scenario is untestable. The lint rule SCENARIO_FOR_REQ catches this.
- **Contracts are bidirectional** — if Service A `triggers` event E, Service B must `accepts` event E. The graph should show both sides.
- **Archive doesn't delete** — archived changes preserve their edges. The `superseded_by` chain is your audit trail.
- **Progressive rigor** — not every change needs a full spec. Start with a change node + requirement + scenario. Add `guarantees`, `fails_with`, `design` only as needed.
- **Spec graph is source of truth, not documentation** — if the code and the spec disagree, the spec wins. Update the spec to match reality, then regenerate.
- **NebulaGraph: `change` is a reserved word in nGQL** — when syncing to NebulaGraph, `kind: change` nodes map to the `delta` tag (see `KIND_TO_TAG` in sync script). The markdown files keep `kind: change`. See `knowledge-graph` skill's `references/nebulagraph-integration.md`.
- **Lint script generator expressions need `for` clause** — `spec-lint.py`'s `check_consistent_fallbacks` had a bug: `any(e.source == ...)` without a trailing `for e in g.edges`. Python's `any()`/`all()` with a generator expression silently returns `False` on an undefined loop variable instead of raising, making the rule always pass. Always include `for item in iterable` in generator expressions passed to `any()`/`all()`.
- **SQLAlchemy: `metadata` is a reserved column name** — SQLAlchemy's `declarative_base()` reserves `metadata` for the `Base.metadata` object. Naming a column `metadata` raises `InvalidRequestError` at class definition time. Use `meta_json` or `extra` for JSON metadata columns. This error surfaces immediately at import time, not at runtime, which is helpful but confusing if you don't know the cause.
- **Generated code must avoid PEP 604 type annotations** — Python 3.9 doesn't support `X | None` syntax (PEP 604). When generating Python code from specs, use `Optional[X]` or remove the return annotation entirely. This applies to any code the agent writes during Phase 7 — models, routes, sync scripts. Already documented in `knowledge-graph` gotcha #6; cross-reference before writing implementation code.
- **Edge deduplication during sync** — When implementing a sync engine that parses |rel:| edges from markdown and inserts them into a relational DB, deduplicate the parsed edges before insertion. A single file may have the same edge declared twice (copy-paste artifact). Without dedup, a UNIQUE constraint on (from_node_id, predicate, to_node_id) will fire. Always call set() on the parsed edge tuples before inserting.
- **After building spec tooling, shift to building applications** — The spec-graph methodology's value is producing production applications, not tools for its own sake. After implementing the core spec-to-code pipeline (models, routes, sync), do NOT keep building supporting tools (dashboards, linters, analyzers). Ask the user immediately: what application should we build from these specs? The dashboards are windows — the output is the app.
- **React list filter: don't reset page on page change** — When implementing a filterable, paginated list view, the `setFilter` function must NOT reset the page parameter when changing the page itself. Common bug pattern:
  ```jsx
  // BAD — always resets to page 1, even for page changes
  const setFilter = (key, value) => {
    const next = new URLSearchParams(searchParams);
    next.set(key, value);
    next.set('page', '1');  // ← breaks pagination
  };

  // GOOD — only reset page for non-page filter changes
  const setFilter = (key, value) => {
    const next = new URLSearchParams(searchParams);
    next.set(key, value);
    if (key !== 'page') next.set('page', '1');
  };
  ```
- **Keep shared repos professional — no personal content** — When packaging the spec graph for public or team sharing, strip personal content: belief systems, philosophy, hardware specs, personal preferences, individual behavioral data, and any nodes referencing the author. The repo should be adoptable by anyone without context about who built it. Run grep -rli for personal names, beliefs, and identifying details before publishing.
- **Avoid bureaucratic overbranding** — Labels like Center of Excellence, Enterprise Framework, or Certified Methodology create adoption friction and make the methodology feel like corporate overhead rather than a practical tool. Use neutral professional language in documentation. Let the methodology speak for itself — if it is useful, people will adopt it without branding.

## Build Learnings (from real spec-driven development)

These are lessons from building the IG Scraper Platform from its spec graph. Each maps to a spec graph pattern.

### Learning 1: External constraints belong in the graph as `constrains` edges

Instagram's JSON endpoint (`?__a=1&__d=1`) was blocked in production (May 2026). This broke `profile-spider`. The fix was to model it as a constraint node:

```
instagram-blocks-json-endpoint (concept)
  └── constrains → profile-spider (requirement)
```

Now any agent that reads the subgraph knows: "This requirement is constrained by Instagram's anti-bot measures." The fix is encoded alongside the requirement, not lost in a Slack thread.

**Pattern:** When an external service blocks/limits a requirement, create a concept node and link it with `constrains`. Future agents see the constraint and generate fallback logic automatically.

### Learning 2: Multi-strategy fallback is a graph pattern

The spider evolved from single-strategy to multi-strategy:
1. Try JSON endpoint (fast path)
2. Fallback to HTML parsing (extract `window._sharedData`)
3. If both fail, return clear error with fix instructions

This maps to the graph as:
```
profile-spider
  └── depends_on → json-endpoint-strategy (concept)
  └── depends_on → html-parse-strategy (concept)  
  └── depends_on → test-mode (concept)
```

**Pattern:** Requirements that depend on unreliable external services should have multiple strategy nodes as children. The agent generates the fallback chain from the dependency graph.

### Learning 3: Test mode is a first-class spec concept

Real scraping requires auth/proxies. For pipeline demos and CI, we need `test_mode=True` that returns mock data. This isn't a hack — it's a spec requirement:

```
test-mode (concept)
  └── enables → pipeline-demo (requirement)
  └── enables → ci-verification (requirement)
```

**Pattern:** Every spec that touches external services should have a `test-mode` concept linked to it. The code generator should check for this edge and produce `test_mode` parameter support automatically.

### Learning 4: Failures become nodes — not comments

Every failure during the build produced a knowledge graph node:
- `instagram-blocks-json-endpoint` — the constraint
- `scraper-fallback-strategy` — the fix pattern  
- `test-mode` — the demo enabler

This means the next agent that builds from this spec graph won't repeat the same failures. The graph is self-improving.

**Pattern:** After every build session, ingest failures as concept nodes linked to the requirements they constrain. The graph becomes a living incident log.

### Learning 5: Start server, test pipeline, fix, iterate — in that order

The build sequence that works:
1. Write spec graph (markdown, no code)
2. Write spiders with test_mode first (verify pipeline before real work)
3. Write API (TestClient before uvicorn)
4. Deploy (uvicorn), hit failure, add constraint to graph, fix code
5. Sync to NebulaGraph (spec → code traceability)

**Anti-pattern:** Writing all code first then testing. We'd have missed the Instagram endpoint block until production. The test_client caught it immediately.

### Learning 6: Dependency-ordered implementation for web apps

Building a multi-component web app from a spec graph should follow the dependency chain:

1. **Data models first** — `models.py` (no dependencies). SQLAlchemy tables with indexes.
2. **Sync/bridge layer second** — reads markdown, writes to DB (depends on models only).
3. **API layer third** — FastAPI routes (depends on models + sync).
4. **Frontend last** — React SPA consuming the API (no backend dependencies).

This ordering means at each step you can verify: models via direct SQL queries, sync by examining the DB, API via curl/TestClient, frontend via the browser. Each layer is testable before the next begins.

**Anti-pattern:** Scaffolding the frontend before the API is ready. You end up mocking data and rewriting when the real API shape differs.

**Anti-pattern:** Writing API routes before the data model is stable. Every model change cascades into route changes.

### Learning 8: Non-web apps follow the same lifecycle — sub-specs shape differs

The ASCII shooter game (C + raylib) proved the methodology works for non-web applications. The 8-phase lifecycle, predicate system, and file structure were identical. What changed was the sub-spec decomposition:

| Web App Sub-Specs | Game Sub-Specs |
|---|---|
| API Layer | Player System |
| Data Model | Enemy System |
| Sync Engine | Level Design |
| Dashboard/UI | Weapons & Power-ups |
| — | Boss System |
| — | Rendering Engine |

The spec predicates used also differ:
- **Web apps** use `exposes`/`accepts`/`returns` heavily (API contracts), `deploys_to`, `authenticates_via`
- **Games** use `contains` (hierarchical system decomposition), `constrains` (design constraints like ASCII grid rendering, C99 struct limits), and `scenario_for` (Given-When-Then for enemy AI behavior)

**Pattern:** The lifecycle and storage format are framework-agnostic. Only the predicate vocabulary shifts based on the application type. API contracts (`exposes`/`accepts`/`returns`) are web-heavy; constraint modeling (`constrains`/`enables`/`blocks`) is universal.

**Pattern:** Phase 0 for creative/entertainment projects should use multiple-choice clarifies (genre → sub-genre → scope) which converge in 3 rounds. Phase 0 for business/operations projects should use open-ended workflow questions (5-7 rounds). Both ingest answers into the graph immediately.

**Anti-pattern:** Assuming every project needs a database, API layer, and frontend. A game spec has different architectural layers (input → update → render → audio) that don't map to web API patterns. Don't force-fit web architecture onto non-web projects.

### Learning 9: Spec-driven development works without an AI agent

The repo at github.com/Koustubh8/spec-engine is fully standalone. A human developer can:
1. Clone the repo
2. Read the spec graph (342 markdown files)
3. Run `tools/knowledge-graph/query.py` and `tools/knowledge-graph/lint.py` directly (no Hermes Agent needed)
4. Run `tools/spec-studio/backend/prod_lint.py` for production readiness
5. Build from specs manually

The methodology and tooling are independent of the AI agent that authored them. This was a design goal — the spec graph is human-readable and tool-independent. Any developer with Python + git can work with it.

For knowledge-graph-backed web apps, the cleanest architecture is:
- **Source of truth**: markdown files with YAML frontmatter and `|rel:|` edges (unchanged, editable via vim/scripts)
- **Query layer**: SQLAlchemy tables synced from markdown via a sync engine (fast indexed lookups, pagination, graph traversal)

The sync engine is the key component. Design it to:
- Walk files, check mtime → skip unchanged (incremental sync)
- Parse YAML frontmatter → derive slug from filename, kind from directory
- Parse `|rel:|` edges → deduplicate before insert
- Use delete+reinsert for edges per node (simpler than diffing)
- Create placeholder reference nodes for unresolved edge targets
- Maintain a `sync_runs` audit table for status tracking
- Handle Python 3.9 type annotation compatibility (no `X | None`)

The sync engine spec (`sync-engine-spec`) should include requirements for: `incremental-sync`, `edge-reconciliation`, `error-tolerant-parsing`, `sync-run-logging`.

## NebulaGraph Backend

The spec graph can be synced to NebulaGraph for Cypher queries, visualization, and code generation. See the `knowledge-graph` skill's `references/nebulagraph-integration.md` for full setup.

Quick start after NebulaGraph is running:
```bash
# Sync markdown specs to NebulaGraph
python3 ~/mywork/nebula/sync_markdown_to_nebula.py

# Verify spec lint rules
python3 scripts/spec-lint.py

# Generate FastAPI code from a spec subgraph
python3 ~/mywork/nebula/gen_fastapi.py specs/auth-spec
```

**NebulaGraph Studio (visualization):** http://localhost:7001 — connect with host `graphd:9669`, user `root`, password `nebula`, select space `knowledge_graph`.

**NebulaGraph Query Reference:** See `references/nebula-advanced-queries.md` for 10 query patterns covering lifecycle traces, impact analysis, reusable inventory, missing edge detection, change history, dependency graphs, file traceability, implementation coverage, graph health, and Vedanta lineage queries. Includes a quick-reference cheat sheet.

## References

- [OpenSpec Analysis](references/openspec-analysis.md) — Deep-dive comparison of Fission-AI/OpenSpec vs our graph-native approach.
- [NebulaGraph Advanced Queries](references/nebula-advanced-queries.md) — 10 query patterns + cheat sheet for the knowledge-graph NebulaGraph backend.
- [Spec Studio Worked Example](references/spec-studio-worked-example.md) — Complete end-to-end lifecycle walkthrough from this session. 31 nodes, 48 edges, 4 specs, 19 requirements. Shows the exact commands and decision flow for each phase.
- [FastAPI Web App Build Recipe](references/fastapi-webapp-build-recipe.md) — Implementation-side reference: how to translate a spec graph into a running FastAPI + SQLAlchemy + React application. Covers the dual-mode sync engine design, model gotchas (reserved column names, PEP 604), and layered build order.
- [Production Readiness Linter Guide](references/prod-readiness-linter-guide.md) — 12-rule linter that checks a spec graph for production-readiness gaps (logging, error handling, health endpoints, CORS, timeouts, retries, config externalization, migrations, environments, monitoring, CI). Includes rule implementation pattern, score bands, API response format, and integration instructions.
- [Repository Packaging Guide](references/repo-packaging-guide.md) — How to package the spec-graph methodology as a professional, shareable GitHub repository. Repository structure, what to include/avoid, README tone, and publishing criteria. Uses neutral professional language — no bureaucratic overbranding.
