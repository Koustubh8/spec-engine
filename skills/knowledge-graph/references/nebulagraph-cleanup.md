# NebulaGraph Cleanup

When content is removed from the markdown knowledge graph (e.g. stripping personal data for a public repo), NebulaGraph still retains the old vertices and edges because the sync script only INSERTS — it does not DELETE removed nodes.

## Full Re-sync Procedure

```bash
# 1. Drop and recreate the space (erases all data)
docker run --rm --network nebula_default vesoft/nebula-console:v3.8.0 \
  -addr graphd -port 9669 -u root -p nebula \
  -e "DROP SPACE IF EXISTS knowledge_graph;"

sleep 3

docker run --rm --network nebula_default vesoft/nebula-console:v3.8.0 \
  -addr graphd -port 9669 -u root -p nebula \
  -e "CREATE SPACE knowledge_graph(partition_num=1, replica_factor=1, vid_type=FIXED_STRING(64));"

# 2. Re-initialize tags and edge types
cd ~/mywork/nebula
python3 nebula_init.py

# 3. Re-sync from cleaned markdown source
KNOWLEDGE_PATH=/path/to/cleaned/knowledge-graph python3 sync_markdown_to_nebula.py
```

## Verify Cleanup

```bash
# Check no personal content remains
docker run --rm --network nebula_default vesoft/nebula-console:v3.8.0 \
  -addr graphd -port 9669 -u root -p nebula \
  -e "USE knowledge_graph; MATCH (n) WHERE n.title CONTAINS 'personal_name' RETURN count(n);"
```

## Why DROP SPACE is needed

The sync script (`sync_markdown_to_nebula.py`) only inserts new vertices and edges. It does not diff against the existing graph and remove stale entries. A full space drop + recreate is the only reliable way to clean NebulaGraph without manual DELETE queries for every removed node.

## Avoiding stale state

If you regularly clean the markdown source, add this to your sync workflow:

```bash
# Before sync: drop + recreate
# After sync: verify with stats
```
