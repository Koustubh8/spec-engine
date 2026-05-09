# Predicate Vocabulary

All 29 predicates in the Spec Engine system. Every predicate has a direction, a semantic meaning, and an inverse.

## Universal Predicates (Identity, Belief, Influence)

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `is_a` | sub → obj | X is a type of Y | `instance_of` |
| `same_as` | sub ↔ obj | X is also known as Y | `same_as` |
| `portion_of` | sub → obj | X is part of Y | `contains` |
| `influences` | sub → obj | X shapes Y | `influenced_by` |
| `depends_on` | sub → obj | X needs Y | `depended_by` |
| `uses` | sub → obj | X employs Y as tool | `used_by` |
| `builds` | sub → obj | X creates/develops Y | `built_by` |
| `produces` | sub → obj | X generates Y | `produced_by` |
| `teaches` | sub → obj | X instructs Y | `taught_by` |
| `attests` | sub → obj | X confirms/teaches Y | `attested_by` |
| `contradicts` | sub ↔ obj | X and Y are inconsistent | `contradicts` |
| `follows` | sub → obj | X practices/adheres to Y | `followed_by` |
| `values` | sub → obj | X holds Y in high regard | `valued_by` |
| `prefers` | sub → obj over target | X prefers Y over Z | `preferred_by` |
| `rejects` | sub → obj | X actively avoids Y | `rejected_by` |
| `constrains` | sub → obj | X limits Y | `constrained_by` |
| `enables` | sub → obj | X makes Y possible | `enabled_by` |
| `blocks` | sub → obj | X prevents Y | `blocked_by` |
| `has_instance` | sub → obj | X has a known instance Y | `instance_of` |

## Specification Predicates

### Contract Predicates

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `exposes` | spec → endpoint | Spec exposes an API endpoint | `exposed_by` |
| `accepts` | endpoint → schema | Endpoint accepts input schema | `accepted_by` |
| `returns` | endpoint → schema | Endpoint returns output schema | `returned_by` |
| `triggers` | event → action | Event triggers a downstream action | `triggered_by` |
| `fails_with` | condition → error | Condition produces an error response | `failed_by` |

### Structure Predicates

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `spec_of` | spec → component | Spec describes a software component | `spec_of` |
| `contains` | spec → requirement | Spec contains a requirement | `portion_of` |
| `scenario_for` | scenario → requirement | Scenario tests/validates a requirement | `has_scenario` |

### Change/Delta Predicates

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `change_for` | change → spec | Change targets a spec for modification | `has_change` |
| `adds` | change → requirement | Change introduces a new requirement | `added_by` |
| `modifies` | change → requirement | Change alters an existing requirement | `modified_by` |
| `removes` | change → requirement | Change eliminates a requirement | `removed_by` |
| `archives_to` | change → spec | Change is merged/archived into a spec | `archived_from` |
| `supersedes` | change → change | Change replaces a previous version | `superseded_by` |

### Deployment Predicates

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `deploys_to` | component → target | Component runs on deployment target | `deployed_by` |
| `authenticates_via` | component → method | Component authenticates using method | `authenticator_for` |
| `touches` | task → file | Task modifies a specific source file | `touched_by` |
| `shares_schema_with` | comp ↔ comp | Components share a database schema | `shares_schema_with` |

### Verification Predicates

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `tests` | test → requirement | Test verifies a requirement | `tested_by` |
| `guarantees` | component → property | Component guarantees a property | `guaranteed_by` |
| `implements` | code → spec | Code implements a spec | `implemented_by` |
| `conforms_to` | artifact → standard | Artifact conforms to a standard | `conformed_by` |

### Reuse Predicate

| Predicate | Direction | Meaning | Inverse |
|-----------|-----------|---------|---------|
| `reuses` | project → pattern | Project leverages a reusable pattern | `reused_by` |

## Ternary Predicate

`prefers` is the only ternary predicate — it requires a comparison target:

```
user prefers postgres --over mysql
```

This is handled by the `--over` CLI flag in `ingest.py` and stored in the edge's `properties` JSON column.

## Adding a New Predicate

1. Add to `standards/predicate-vocabulary.md`
2. Add to `tools/knowledge-graph/SCHEMA.md`
3. Add to `INVERSE_MAP` in `tools/knowledge-graph/graph.py`
4. Add to `INVERSE_MAP` in `tools/spec-studio/backend/sync.py`
5. If using NebulaGraph: `CREATE EDGE IF NOT EXISTS predicate_name(description STRING);`
