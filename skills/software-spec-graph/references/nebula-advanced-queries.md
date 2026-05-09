# NebulaGraph Advanced Query Reference

> Query patterns for the knowledge-graph + spec-graph NebulaGraph backend.
> All queries assume `USE knowledge_graph;` is already executed.
> Space: `knowledge_graph` · Graphd: `graphd:9669` · Studio: `http://localhost:7001`

---

## 1. Full Lifecycle Trace

**Purpose:** Trace a requirement from exploration → decision → spec → implementation → archive.

```cypher
-- Full lifecycle from exploration change to running code
MATCH p=(e:delta)-[:change_for|:adds|:supersedes|:enables|:implements|:archives_to*1..5]->(x)
WHERE id(e) == "changes/explore-ig-scraper"
RETURN p
```

**Variant: trace requirement → touched files**
```cypher
MATCH p=(req:requirement)<-[:adds]-(ch:delta)-[:adds]->(t:task)-[:touches]->(f)
WHERE id(req) == "requirements/dark-mode-requirement"
RETURN req, ch, t, f
```

**Explanation:** Each hop is a different phase. The `*1..5` allows variable-length paths so you see the complete chain in one query.

---

## 2. Impact Analysis

**Purpose:** "What breaks if I change X?"

```cypher
-- Everything that depends on a spec (2 hops)
MATCH (s:spec)-[*1..2]->(d)
WHERE id(s) == "specs/auth-spec"
RETURN s, d
```

```cypher
-- Reverse: what depends ON a spec?
MATCH (d)-[*1..2]->(s:spec)
WHERE id(s) == "specs/auth-spec"
RETURN s, d
```

```cypher
-- Contracts that touch a specific endpoint
MATCH (s:spec)-[:exposes]->(e)-[:accepts|:returns|:fails_with]->(c)
WHERE id(s) == "specs/auth-spec"
RETURN s, e, c
```

**When to use:** Before modifying any spec, run this to see blast radius. Especially powerful before deleting or modifying a shared dependency.

---

## 3. Reusable Pattern Inventory

**Purpose:** "What do we already have that I can reuse?"

```cypher
-- All reusable patterns
MATCH (rp:concept)<-[:is_a]-(p:concept)
WHERE id(rp) == "concepts/reusable-pattern"
RETURN id(p) AS pattern, p.title AS title
```

```cypher
-- Which projects reuse which patterns?
MATCH (proj:project)-[:reuses]->(p:concept)-[:is_a]->(rp:concept)
WHERE id(rp) == "concepts/reusable-pattern"
RETURN id(proj) AS project, id(p) AS pattern
ORDER BY project
```

```cypher
-- Find patterns by tag (e.g., all "payment" patterns)
MATCH (p:concept)-[:is_a]->(:concept)
WHERE id(p) =~ ".*payment.*" OR id(p) =~ ".*triage.*" OR id(p) =~ ".*dashboard.*"
RETURN id(p) AS pattern
```

**When to use:** ALWAYS. First query of any new exploration phase. Run before proposing new specs.

---

## 4. Missing Edge Detection (Spec-Lint as Cypher)

**Purpose:** Find specs that break lint rules — directly in NebulaGraph.

```cypher
-- AUTH_SPECIFIED: specs with exposes but no authenticates_via
MATCH (s:spec)-[:exposes]->(e)
WHERE NOT (s)-[:authenticates_via]->()
RETURN id(s) AS spec, id(e) AS endpoint
```

```cypher
-- DEPLOYMENT_SPECIFIED: specs with exposes but no deploys_to
MATCH (s:spec)-[:exposes]->(e)
WHERE NOT (s)-[:deploys_to]->()
RETURN id(s) AS spec, id(e) AS endpoint
```

```cypher
-- SCENARIO_FOR_REQ: requirements with no scenarios
MATCH (r:requirement)
WHERE NOT (r)<-[:scenario_for]-()
RETURN id(r) AS requirement
```

```cypher
-- NO_ORPHAN_REQUIREMENTS: requirements not contained in any spec
MATCH (r:requirement)
WHERE NOT (r)<-[:contains]-() AND NOT (r)<-[:adds]-()
RETURN id(r) AS orphan
```

```cypher
-- GUARANTEES_HAS_TESTS: guarantees with no tests
MATCH (n)-[:guarantees]->()
WHERE NOT (n)<-[:tests]-()
RETURN id(n) AS node
```

**When to use:** Before archiving any change. Run the full suite. Equivalent to `spec-lint.py` but in Cypher.

---

## 5. Change History & Audit Trail

**Purpose:** "What changed, when, and why?"

```cypher
-- All changes archived to a spec (OpenSpec archive chain)
MATCH (ch:delta)-[:archives_to]->(s:spec)
WHERE id(s) == "specs/ig-scraper-platform"
RETURN id(ch) AS change, ch.title AS title
ORDER BY ch.title
```

```cypher
-- All findings from an exploration (what did we learn?)
MATCH (e:delta)-[:adds]->(f:concept)
WHERE id(e) == "changes/explore-candle-crm"
RETURN id(f) AS finding
```

```cypher
-- Findings that constrain sub-problems (what shapes what?)
MATCH (f:concept)-[:constrains]->(sp:concept)
WHERE id(f) =~ ".*finding.*" OR id(f) =~ ".*concern.*"
RETURN id(f) AS constraint, id(sp) AS constrains
```

**When to use:** Understanding why a spec looks the way it does. Trace any requirement back to the exploration finding that shaped it.

---

## 6. Dependency Graph

**Purpose:** "What depends on what?"

```cypher
-- Direct dependencies between specs
MATCH (a:spec)-[:depends_on]->(b:spec)
RETURN id(a) AS component, id(b) AS depends_on
```

```cypher
-- Full dependency tree (2 hops)
MATCH p=(a:spec)-[:depends_on*1..2]->(b:spec)
RETURN p
```

```cypher
-- Components and their tools
MATCH (s:spec)-[:uses|:depends_on]->(t:tool)
RETURN id(s) AS spec, id(t) AS tool
ORDER BY spec
```

**When to use:** Architecture diagrams. Shows the component graph for any platform spec.

---

## 7. File Traceability

**Purpose:** "Which files does this change touch?"

```cypher
-- Requirement → change → task → file
MATCH (req:requirement)<-[:adds]-(ch:delta)-[:adds]->(t:task)-[:touches]->(f)
WHERE id(req) == "requirements/dark-mode-requirement"
RETURN id(req), id(ch), id(t), id(f)
```

```cypher
-- Reverse: which requirements affect this file?
MATCH (f)<-[:touches]-(t:task)<-[:adds]-(ch:delta)-[:adds]->(req:requirement)
WHERE id(f) == "references/frontend-index-html"
RETURN id(f), id(t), id(ch), id(req)
```

**When to use:** Change request impact analysis. "If I change the auth requirement, which files need updating?" → exact answer.

---

## 8. Implementation Coverage

**Purpose:** "Which specs are actually built?"

```cypher
-- Specs with implementations
MATCH (impl)-[:implements]->(s:spec)
RETURN id(s) AS spec, id(impl) AS implemented_by
```

```cypher
-- Specs WITHOUT implementations (spec gap)
MATCH (s:spec)
WHERE NOT (s)<-[:implements]-()
RETURN id(s) AS unimplemented_spec
```

```cypher
-- Requirement coverage: specs → requirements → scenarios → tests
MATCH (s:spec)-[:contains]->(r:requirement)
OPTIONAL MATCH (r)<-[:scenario_for]-(sc:scenario)
OPTIONAL MATCH (r)<-[:tests]-(t)
RETURN id(s) AS spec, id(r) AS requirement,
       count(DISTINCT sc) AS scenarios, count(DISTINCT t) AS tests
```

**When to use:** Sprint planning. Shows exactly what's built vs what's spec'd but not implemented.

---

## 9. Graph Health & Stats

**Purpose:** "How big is the graph? What's in it?"

```cypher
-- Total vertices and edges
MATCH (v) RETURN count(v) AS vertices
UNION ALL
MATCH ()-[e]->() RETURN count(e) AS edges
```

```cypher
-- Node count by kind (tag)
MATCH (v) RETURN id(v) AS kind LIMIT 1  -- placeholder
-- NebulaGraph doesn't support RETURN type() directly for tags.
-- Use Python instead: for kind in KIND_TO_TAG: MATCH (v:kind) RETURN count(v)
```

```cypher
-- Edge type distribution
-- Run via Python: for each edge type, MATCH ()-[e:type]->() RETURN count(e)
```

```cypher
-- Most connected nodes (centrality)
MATCH (n)-[e]-()
RETURN id(n) AS node, count(e) AS degree
ORDER BY degree DESC LIMIT 10
```

---

## 10. Vedanta Lineage Queries

**Purpose:** Transmission chain. Path finding through spiritual lineage.

```cypher
-- Sri Ramakrishna to Koustubh (the transmission chain)
MATCH p=(a:person)-[*1..5]->(b:person)
WHERE id(a) == "people/sri-ramakrishna"
  AND id(b) == "people/koustubh"
RETURN p
```

```cypher
-- All concepts taught by the Upanishads
MATCH (u)-[:teaches]->(c:concept)
WHERE id(u) =~ ".*upanishad.*"
RETURN id(u) AS upanishad, id(c) AS concept
```

```cypher
-- Prasthanatrayi (triple canon)
MATCH (text)-[:attests]->(v:concept)
WHERE id(v) == "concepts/vedanta"
  AND id(text) =~ ".*upanishad|.*gita|.*sutra.*"
RETURN id(text) AS scripture
```

---

## Query Tips

1. **Use `id()` for exact match.** String VIDs like `"specs/auth-spec"` need exact matching. Partial matching with `=~` is slower but useful for pattern searches.

2. **Use `LIMIT` aggressively.** On 200+ node graphs, unlimited traversals can be slow. Cap at 100.

3. **Use `OPTIONAL MATCH` for coverage queries.** When you want to see missing edges (e.g., requirements with no scenarios), use OPTIONAL MATCH with count.

4. **Variable-length paths are powerful but expensive.** `[*1..5]` on 500+ edges can be slow. Start with `[*1..2]` and expand if needed.

5. **Studio visualization tip:** After any MATCH that returns `p`, switch to graph view to see the visual subgraph. Click nodes to expand.

6. **Python bridge:** For complex queries, use `python3 -c "..."` with the nebula3 client. The sync script at `~/mywork/nebula/sync_markdown_to_nebula.py` shows the pattern.

7. **Sync before querying:** Always run `python3 ~/mywork/nebula/sync_markdown_to_nebula.py` before querying in NebulaGraph to ensure markdown changes are reflected.

---

## Query Cheat Sheet (Quick Reference)

```
WHAT YOU WANT                    CYPHER PATTERN
───────────────────────────────  ─────────────────────────────────
Impact: what depends on X?       MATCH (s)-[*1..2]->(d) WHERE id(s)=="X"
Reuse: available patterns?       MATCH (p)-[:is_a]->(:concept{title:"Reusable Pattern"})
Missing auth?                    MATCH (s:spec)-[:exposes]->() WHERE NOT (s)-[:authenticates_via]->()
Change history?                  MATCH (ch:delta)-[:archives_to]->(s) WHERE id(s)=="X"
Which files change?              MATCH (t:task)-[:touches]->(f) WHERE ...
Unimplemented specs?             MATCH (s:spec) WHERE NOT (s)<-[:implements]-()
Most connected nodes?            MATCH (n)-[e]-() RETURN id(n), count(e) ORDER BY count(e) DESC
Full lifecycle?                  MATCH p=(e:delta)-[*1..5]->(x) WHERE id(e)=="changes/explore-X"
Exploration findings?            MATCH (e:delta)-[:adds]->(f) WHERE id(e)=="changes/explore-X"
Dependency graph?                MATCH (a:spec)-[:depends_on]->(b:spec)
```
