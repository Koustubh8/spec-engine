---
name: tools-for-project
kind: query
created: 2026-05-08
updated: 2026-05-08
query_type: path
params: {"from": "project", "to": "tool"}
---

# Query: Tools for a Project

Find all tools used directly or indirectly by a given project.

## Usage

```bash
# Find all tools the options-screener uses
python3 ~/.hermes/skills/research/knowledge-graph/scripts/query.py options-screener --via uses --depth 2
```
