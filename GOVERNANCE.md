# Governance

## Decision-Making Framework

### Change Types and Approval

| Change Type | Approval | Reviewers | Timeline |
|-------------|----------|-----------|----------|
| New predicate | CoE maintainers + 1 approval | 2 | 3 days |
| New node kind | CoE maintainers + 1 approval | 2 | 3 days |
| Lint rule change | CoE maintainers + 2 approvals | 3 | 5 days |
| Tooling improvement | PR review + CI passing | 1 | 1 day |
| Spec contribution (new project) | PR review + lint passing | 1 | 2 days |
| Documentation | PR review | 1 | 1 day |
| Breaking methodology change | CoE vote + 3 approvals | 5 | 7 days |

### Adding a New Predicate

1. Add to `standards/predicate-vocabulary.md` (definition, direction, inverse)
2. Add to `tools/knowledge-graph/SCHEMA.md`
3. Add to `INVERSE_MAP` in `tools/knowledge-graph/graph.py`
4. Add to `INVERSE_MAP` in `tools/spec-studio/backend/sync.py`
5. If using NebulaGraph: `CREATE EDGE IF NOT EXISTS new_predicate(description STRING);`
6. Update all query patterns that filter by predicate
7. Submit PR with all changes in a single commit

### Adding a New Node Kind

1. Add to `standards/node-kinds.md`
2. Add to `VALID_NODE_KINDS` in `tools/spec-studio/backend/models.py`
3. Add plural mapping to `PLURAL_MAP` in `tools/spec-studio/backend/sync.py`
4. Add to `KIND_NORMALIZE` in sync.py
5. Add NebulaGraph tag mapping in `tools/nebula/sync_markdown_to_nebula.py`
6. Submit PR

### Versioning

We follow semantic versioning:

- **Major**: Breaking changes to the predicate system or methodology
- **Minor**: New predicates, node kinds, lint rules, or tooling features
- **Patch**: Bug fixes, documentation, non-breaking improvements

## Quality Gates

### PR Checklist

Every PR must pass:
- [ ] `tools/knowledge-graph/lint.py` — no orphan nodes, broken edges
- [ ] `tools/spec-studio/backend/prod_lint.py` — score ≥ 10/12 for deployable projects
- [ ] All existing tests pass
- [ ] New predicates/kinds documented in standards/
- [ ] README updated if applicable

### Release Criteria

A release is cut when:
- All lint rules pass (0 errors, 0 warnings on core spec)
- Production readiness score ≥ 10/12 on self-spec
- No known broken edges in the knowledge graph
- All documentation is up to date

## Roles

| Role | Responsibility |
|------|---------------|
| **CoE Maintainer** | Reviews PRs, approves predicate/kink changes, manages releases |
| **Contributor** | Submits specs, tools, and documentation via PR |
| **Reviewer** | Reviews PRs for correctness and methodology adherence |
| **User** | Consumes the methodology and tooling, provides feedback |
