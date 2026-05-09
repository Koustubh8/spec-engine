# Contributing

## How to Contribute a Spec (for a new project)

1. **Fork** this repository
2. **Read** the methodology: `templates/` and `standards/lifecycle.md`
3. **Create** spec files in `knowledge-graph/` following the templates
4. **Run lint** to verify:
   ```bash
   cd tools/knowledge-graph
   python3 lint.py   # No orphan nodes, no broken edges
   ```
5. **Run spec lint** to check completeness:
   ```bash
   cd ../spec-studio/backend
   python3 spec-lint.py   # All requirements have scenarios
   ```
6. **Run prod lint** to check readiness:
   ```bash
   python3 prod_lint.py   # Score ≥ 10/12 for production projects
   ```
7. **Submit a PR** with:
   - All new spec files in `knowledge-graph/`
   - A README in `examples/your-project/` describing the project
   - Lint results in the PR description

### Spec Authoring Guidelines

- **One concept per node.** "RAM" and "Random Access Memory" should be linked via `same_as`, not duplicated.
- **Bidirectional consistency.** Every edge automatically creates its inverse. Verify with `query.py`.
- **Slugs are kebab-case.** `swami-vivekananda`, `marketing-mix-modeling`, not `SwamiVivekananda`.
- **Tags are lowercase.** `[ml, marketing, causal]`, not `[ML, Marketing]`.
- **Every requirement needs a scenario.** A SHALL statement without a Given-When-Then is untestable.
- **Don't put implementation in specs.** Specs are WHAT, design nodes are HOW.

## How to Contribute a Tool

1. **Open an issue** describing the tool and what problem it solves
2. **Spec the tool** first using the methodology (the tool should spec itself)
3. **Implement** following the spec
4. **Ensure all edges are added** via `ingest.py` so the tool is linked into the graph
5. **Submit a PR** with both the spec and implementation

## How to Report an Issue

- **Bug**: Include the error output, Python version, and steps to reproduce
- **Feature request**: Describe the gap in the methodology or tooling
- **Spec improvement**: Include the relevant spec file and what's missing

## Code of Conduct

- Be respectful and constructive
- Prefer evidence over opinion (run the linter, show the output)
- Spec changes should be discussed before PRs for major predicate/kink changes
