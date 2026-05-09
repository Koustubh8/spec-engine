# Node Kinds

Every node in the spec graph has a `kind` field that determines its role and valid predicates.

## Core Specification Kinds

| Kind | Purpose | Valid Outgoing Predicates |
|------|---------|--------------------------|
| `spec` | Behavior contract for a component | exposes, accepts, returns, triggers, contains, spec_of, conforms_to |
| `requirement` | A specific behavior (SHALL/MUST/SHOULD) | portion_of, guarantees, depends_on, constrains |
| `scenario` | Given-When-Then example that validates a requirement | scenario_for |
| `change` | Proposed modification (delta) relative to current specs | change_for, adds, modifies, removes, archives_to |

## Design and Concept Kinds

| Kind | Purpose | Valid Outgoing Predicates |
|------|---------|--------------------------|
| `design` | Technical approach document (HOW) | references, depends_on, enables |
| `concept` | Abstract idea, constraint, or architectural decision | constrains, enables, blocks, depends_on, influences |

## Operational Kinds

| Kind | Purpose | Valid Outgoing Predicates |
|------|---------|--------------------------|
| `task` | Implementation checklist item | touches, depends_on, portion_of |
| `tool` | Technology or software component | uses, depends_on, produces |

## Organizational Kinds

| Kind | Purpose | Valid Outgoing Predicates |
|------|---------|--------------------------|
| `person` | Individual human | follows, values, prefers, rejects, uses, builds, influences, goals_for |
| `organization` | Group or institution | produces, values, teaches |
| `reference` | External source or standard | attests, contradicts, teaches |

## Kind-Specific Rules

- **spec**: Must have at least one `contains` edge to a requirement. Exposed specs must have `deploys_to` (lint rule: DEPLOYMENT_SPECIFIED).
- **requirement**: Must have at least one `scenario` node with `scenario_for` edge (lint rule: SCENARIO_FOR_REQ).
- **change**: Must have at least one of `adds`, `modifies`, or `removes`. On archive, gets `archives_to` edge.
- **scenario**: Must follow Given-When-Then format in body text.
- **concept**: No required edges. Used for constraints, risks, and architectural rationale.

## File Naming

- Files live in plural directories: `specs/`, `requirements/`, `scenarios/`, `changes/`, `designs/`, `concepts/`
- File slugs are kebab-case, matching the node title in lowercase
- Example: `specs/auth-spec.md` for node title "Auth Specification"
