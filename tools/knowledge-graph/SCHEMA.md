# Knowledge Graph Schema

## Domain
Personal knowledge graph — projects, tools, philosophies, people, and their relationships.
Used as agentic AI memory store for fact retrieval and inference.
Extended with software specification predicates (adapted from OpenSpec).

## Conventions
- File names: lowercase-kebab-case (e.g., `user-authentication.md`)
- Every node file has YAML frontmatter with `title`, `kind`, `created`, `updated`, `tags`
- Edges use format: `|rel:PREDICATE| [[KIND/SLUG]]`
- Every edge should have a bidirectional counterpart (reverse predicate)
- All nodes listed in `index.md` under the correct section
- All actions logged in `log.md`

## Node Kinds
- `person` — individuals
- `organization` — groups, missions, companies
- `concept` — ideas, philosophies, methodologies
- `tool` — software, frameworks, utilities
- `project` — work products, apps, analyses
- `reference` — books, videos, articles
- `spec` — software specification (component behavior contract)
- `requirement` — a specific behavior a system must have
- `scenario` — Given-When-Then example of a requirement
- `change` — proposed modification to a spec (delta)
- `design` — technical approach document
- `task` — implementation checklist item

## Universal Predicates

### Identity predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `is_a` | sub → obj | "X is a type of Y" |
| `same_as` | sub ↔ obj | "X is also known as Y" |
| `portion_of` | sub → obj | "X is part of Y" |

### Belief predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `follows` | sub → obj | "X practices/adheres to Y" |
| `values` | sub → obj | "X holds Y in high regard" |
| `rejects` | sub → obj | "X actively avoids Y" |
| `prefers` | sub → obj over target | "X prefers Y over Z" |

### Influence predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `influences` | sub → obj | "X shapes Y" |
| `enables` | sub → obj | "X makes Y possible" |
| `blocks` | sub → obj | "X prevents Y" |

### Dependency predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `depends_on` | sub → obj | "X needs Y" |
| `uses` | sub → obj | "X employs Y as tool" |
| `produces` | sub → obj | "X generates Y" |
| `builds` | sub → obj | "X creates/develops Y" |

### Temporal predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `precedes` | sub → obj | "X happens before Y" |
| `supersedes` | sub → obj | "X replaces Y as authoritative" |

### Source/truth predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `attests` | sub → obj | "X confirms/teaches Y" |
| `contradicts` | sub ↔ obj | "X and Y are inconsistent" |
| `teaches` | sub → obj | "X instructs Y" |

### Goal predicates
| Predicate | Direction | Meaning |
|-----------|-----------|---------|
| `goals_for` | sub → obj | "X desires Y" |
| `constrains` | sub → obj | "X limits Y" |

### Software Specification predicates (OpenSpec-adapted)

#### Contract predicates — define interfaces
| Predicate | Direction | Meaning | Example |
|-----------|-----------|---------|---------|
| `exposes` | sub → obj | Component X offers endpoint Y to the outside world | `UserService exposes POST /users` |
| `accepts` | sub → obj | Endpoint Y accepts input schema Z | `POST /users accepts CreateUserPayload` |
| `returns` | sub → obj | Endpoint Y returns output schema Z | `GET /users returns User[]` |
| `triggers` | sub → obj | Event X causes action Y | `payment_success triggers invoice_generation` |
| `fails_with` | sub → obj | X fails with error condition Y | `invalid_token fails_with HTTP_401` |

#### Spec structure predicates
| Predicate | Direction | Meaning | Example |
|-----------|-----------|---------|---------|
| `spec_of` | sub → obj | Spec X describes component Y | `auth-spec spec_of auth-module` |
| `scenario_for` | sub → obj | Scenario X illustrates requirement Y | `valid-login scenario_for user-auth` |

#### Change/delta predicates (OpenSpec ADDED/MODIFIED/REMOVED)
| Predicate | Direction | Meaning | Example |
|-----------|-----------|---------|---------|
| `change_for` | sub → obj | Change X modifies spec Y | `add-2fa change_for auth-spec` |
| `adds` | sub → obj | Change X adds requirement Y | `add-2fa adds 2fa-requirement` |
| `modifies` | sub → obj | Change X modifies requirement Y | `add-2fa modifies session-expiry` |
| `removes` | sub → obj | Change X removes requirement Y | `add-2fa removes remember-me` |
| `archives_to` | sub → obj | Change X merges into spec Y | `add-2fa archives_to auth-spec` |

#### Verification predicates
| Predicate | Direction | Meaning | Example |
|-----------|-----------|---------|---------|
| `tests` | sub → obj | Test X verifies requirement/scenario Y | `test-login-flow tests user-auth` |
| `guarantees` | sub → obj | Component X guarantees property Y | `idempotency_key guarantees exactly_once` |
| `implements` | sub → obj | Code X implements spec Y | `AuthController implements auth-spec` |
| `conforms_to` | sub → obj | Artifact X conforms to standard Y | `auth-spec conforms_to RFC_6749` |
| `touches` | sub → obj | Task X modifies file Y | `task-1.1 touches frontend/index.html` |
| `deploys_to` | sub → obj | Component X deploys to target Y | `scraper-runner deploys_to k8s-cluster` |
| `shares_schema_with` | sub ↔ obj | Component X shares DB schema with Y | `main-api shares_schema_with prefect-flow` |
| `authenticates_via` | sub → obj | Component X authenticates via method Y | `scraper-api authenticates_via jwt-token` |

## Spec Graph Lint Rules

These rules verify a software spec graph is code-generation ready:

| Rule | Severity | Check |
|------|----------|-------|
| EXPOSES_HAS_CONTRACT | ERROR | Every `exposes` node must have at least one `accepts` or `returns` edge |
| SCENARIO_FOR_REQ | WARNING | Every `requirement` should have at least one `scenario_for` |
| GUARANTEES_HAS_TESTS | ERROR | Every `guarantees` edge should have at least one `tests` edge for the same subject |
| CHANGE_MERGES | INFO | Every `change_for` node should eventually have an `archives_to` edge |
| IMPLEMENTS_SPEC | WARNING | Every `spec_of` should have at least one `implements` from a code node |
| FAILS_WITH_CONTRACT | WARNING | Every `fails_with` should reference a valid error code |
| NO_ORPHAN_REQUIREMENTS | WARNING | Every `requirement` should have a `spec_of` or `adds` from a change |
| TRIGGERS_HAS_HANDLER | WARNING | Every `triggers` edge should have a corresponding handler consuming the event |
| SCHEMA_CONSISTENCY | ERROR | Components that `shares_schema_with` each other MUST have matching table schemas |
| DEPLOYMENT_SPECIFIED | WARNING | Every `spec` SHOULD have a `deploys_to` edge before implementation |
| AUTH_SPECIFIED | WARNING | Every `spec` that `exposes` endpoints SHOULD specify `authenticates_via` |
| CONSISTENT_FALLBACKS | WARNING | Sibling specs with same parent SHOULD use consistent error handling patterns |
| ASYNC_LONG_RUNNING | ERROR | Specs that execute jobs >1s MUST specify async execution strategy |
| EXPLORATION_GATE | ERROR | A `change` node MUST have at least one `adds` edge (finding) before `archives_to` |
| GRAPH_UPDATE_CHECKPOINT | WARNING | After each clarify/explore/critical phase, findings MUST be ingested into graph |
| GRAPH_INVENTORY_CHECK | WARNING | New specs SHOULD reference existing reusable patterns via `reuses` edges |
| REUSE_CHECK | WARNING | Exploration phase SHOULD query `reusable-pattern` node before proposing new specs |

## Page Thresholds
- Create a node when an entity appears in 2+ facts or is central
- Don't create nodes for one-off mentions
- Split a node if it exceeds 50 edges
