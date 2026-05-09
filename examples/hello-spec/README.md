# Hello Spec — Minimal Example

A minimal to-do app spec'd with the Spec Engine methodology. This demonstrates the minimum viable spec for a production-ready application.

## The Spec in 5 Minutes

```bash
cd tools/knowledge-graph

# 1. Create the project
python3 ingest.py "explore-todo" "change_for" "todo-app" --subject-kind changes --object-kind specs

# 2. Decompose
python3 ingest.py "explore-todo" "adds" "todo-crud" --subject-kind changes --object-kind concepts
python3 ingest.py "explore-todo" "adds" "todo-api" --subject-kind changes --object-kind concepts
python3 ingest.py "explore-todo" "adds" "todo-frontend" --subject-kind changes --object-kind concepts

# 3. Query what you created
python3 query.py "todo-app" --depth 2
```

## Result

A spec graph with 1 platform spec, 3 sub-concepts, and 1 exploration change — ready for Phase 2 (constraints).
