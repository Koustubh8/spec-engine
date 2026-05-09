# NebulaGraph Integration

How to run NebulaGraph as the query engine + visualization layer for the knowledge graph.

## Docker Compose

```bash
cd ~/mywork/nebula
docker compose up -d
```

Three containers on first start: `nebula-metad-1`, `nebula-storaged-1`, `nebula-graphd-1`. Adds `nebula-studio-1` (port 7001) for visualization.

Ports: `9669` (graphd), `9559` (metad), `9779` (storaged), `7001` (studio).

## First-Run Gotcha: ADD HOSTS

**Problem:** On fresh deployment, storaged can't register with metad ("Machine not existed!" heartbeat failures). Graphd depends on storaged being healthy, so it won't start either.

**Fix sequence:**

1. Temporarily remove storaged dependency from graphd in docker-compose:
   ```yaml
   depends_on:
     metad:
       condition: service_healthy
     # storaged: condition: service_healthy  ← comment this out
   ```

2. Start all containers. Graphd will start even though storaged is unhealthy.

3. Add the storage host via nebula-console:
   ```bash
   docker run --rm --network nebula_default vesoft/nebula-console:v3.8.0 \
     -addr graphd -port 9669 -u root -p nebula \
     -e 'ADD HOSTS "storaged":9779'
   ```

4. Restart storaged: `docker compose restart storaged`
5. After storaged is healthy, restore the graphd dependency in docker-compose.

This is a known NebulaGraph v3.8.0 issue. The `--local_config=true` flag (used for storaged/graphd) does NOT apply to metad — do not add it there.

## Reserved Words

NebulaGraph nGQL reserves `change` as a keyword. The sync script maps `kind: change` nodes to the `delta` tag. Markdown files keep `kind: change`. The mapping is in `sync_markdown_to_nebula.py`:

```python
KIND_TO_TAG = {
    ...
    "change": "delta", "changes": "delta",
    ...
}
```

Also: `uses` is NOT reserved despite being a common SQL keyword — it works as an edge type name.

## Schema Initialization

After Docker is healthy:

```bash
cd ~/mywork/nebula
python3 nebula_init.py
```

Creates:
- Space: `knowledge_graph` (FIXED_STRING(256) VIDs, partition_num=1, replica_factor=1)
- 12 tags: person, organization, concept, tool, project, reference, spec, requirement, scenario, delta, design, task
- 40 edge types: all predicates from the grammar + their inverses

Wait ~10s after space creation before creating tags/edges — NebulaGraph needs time to initialize the space.

## Sync

```bash
python3 sync_markdown_to_nebula.py [--dry-run] [--knowledge-path ~/mywork/knowledge-graph]
```

Reads all `.md` node files, inserts vertices and edges. Skip rules:
- Kinds not in `KIND_TO_TAG` → skipped
- Predicates not in `ALL_EDGE_TYPES` → skipped  
- Edge targets that don't exist as vertices → skipped (safe to re-run after vertex creation)

Post-sync verification runs: total vertices, total edges, Vedanta path query.

## Visualization (NebulaGraph Studio)

URL: `http://localhost:7001`

Connection:
```
Host:      graphd:9669  (NOT localhost — Studio runs in Docker)
Username:  root
Password:  nebula
Space:     knowledge_graph
```

Sample queries:
```cypher
-- Full Vedanta transmission chain
MATCH p=(:person)-[*1..5]->(:person)
WHERE id(startNode(p))=="people/sri-ramakrishna"
  AND id(endNode(p))=="people/koustubh"
RETURN p

-- IG scraper platform architecture
MATCH p=(:spec)-[*1..2]->(:spec)
WHERE id(startNode(p))=="specs/ig-scraper-platform"
RETURN p

-- File-level change impact
MATCH (req)<-[:adds]-(ch:delta)-[:adds]->(t:task)-[:touches]->(f)
WHERE id(req)=="requirements/dark-mode-requirement"
RETURN req, ch, t, f
```

## Code Generation

```bash
python3 gen_fastapi.py specs/auth-spec
```

Reads the spec subgraph from NebulaGraph via Cypher, generates a FastAPI route handler with Pydantic models and error handling. Contracts come from `exposes`/`accepts`/`returns`/`fails_with` edges.

## Edge Type Gotcha

When adding new predicates to the knowledge graph grammar, you must:
1. Add to `INVERSE_MAP` in `graph.py` (both scripts: skill + nebula sync use it)
2. Add to `SCHEMA.md` 
3. Create edge type in NebulaGraph: `CREATE EDGE IF NOT EXISTS <name>(description STRING);`
4. Re-run sync

If (3) is missed, the sync script skips those edges silently.
