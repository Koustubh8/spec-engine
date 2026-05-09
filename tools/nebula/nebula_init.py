#!/usr/bin/env python3
"""
Initialize NebulaGraph schema for the Knowledge Graph.

Creates:
- Space: knowledge_graph
- Tags (node types): person, organization, concept, tool, project, reference,
                     spec, requirement, scenario, change, design, task
- Edge types: all 34 predicates with their inverses

Usage:
    python3 nebula_init.py [--graphd 127.0.0.1:9669]
"""

import sys
import time
from nebula3.gclient.net import ConnectionPool, SessionPool
from nebula3.Config import Config

GRAPH_HOST = "127.0.0.1"
GRAPH_PORT = 9669
USER = "root"
PASSWORD = "nebula"
SPACE = "knowledge_graph"

# Node kinds → NebulaGraph tags
TAGS = [
    "person", "organization", "concept", "tool", "project", "reference",
    "spec", "requirement", "scenario", "delta", "design", "task",
]

# All predicates → NebulaGraph edge types
# Format: (edge_type_name, forward: bool, description)
EDGE_TYPES = [
    # Identity
    ("is_a",           True,  "X is a type of Y"),
    ("portion_of",     True,  "X is part of Y"),
    ("contains",       True,  "X contains Y (inverse of portion_of)"),
    ("same_as",        True,  "X is also known as Y"),
    # Belief
    ("follows",        True,  "X practices Y"),
    ("values",         True,  "X holds Y in high regard"),
    ("rejects",        True,  "X actively avoids Y"),
    ("prefers",        True,  "X prefers Y over Z"),
    # Influence
    ("influences",     True,  "X shapes Y"),
    ("enables",        True,  "X makes Y possible"),
    ("blocks",         True,  "X prevents Y"),
    # Dependency
    ("depends_on",     True,  "X needs Y"),
    ("uses",           True,  "X employs Y as tool"),
    ("produces",       True,  "X generates Y"),
    ("builds",         True,  "X creates/develops Y"),
    # Temporal
    ("precedes",       True,  "X happens before Y"),
    ("supersedes",     True,  "X replaces Y as authoritative"),
    # Source/truth
    ("attests",        True,  "X confirms/teaches Y"),
    ("teaches",        True,  "X instructs Y"),
    ("contradicts",     True,  "X and Y are inconsistent"),
    # Goal
    ("goals_for",      True,  "X desires Y"),
    ("constrains",     True,  "X limits Y"),
    # Contract (software-spec)
    ("exposes",        True,  "X offers endpoint Y"),
    ("accepts",        True,  "X accepts input schema Y"),
    ("returns",        True,  "X returns output schema Y"),
    ("triggers",       True,  "X causes action Y"),
    ("fails_with",     True,  "X fails with error Y"),
    # Spec structure
    ("spec_of",        True,  "Spec X describes component Y"),
    ("scenario_for",   True,  "Scenario X illustrates requirement Y"),
    # Change/delta
    ("change_for",     True,  "Change X modifies spec Y"),
    ("adds",           True,  "Change X adds requirement Y"),
    ("modifies",       True,  "Change X modifies requirement Y"),
    ("removes",        True,  "Change X removes requirement Y"),
    ("archives_to",    True,  "Change X merges into spec Y"),
    # Verification
    ("tests",          True,  "Test X verifies requirement Y"),
    ("guarantees",     True,  "X guarantees property Y"),
    ("implements",     True,  "Code X implements spec Y"),
    ("conforms_to",    True,  "X conforms to standard Y"),
    # Symmetric
    ("associated_with", True, "X associated with Y"),
]


def wait_for_graph(host, port, timeout=120):
    """Wait for NebulaGraph to be ready."""
    print(f"Waiting for NebulaGraph at {host}:{port}...")
    config = Config()
    pool = ConnectionPool()
    pool.init([(host, port)], config)

    start = time.time()
    while time.time() - start < timeout:
        try:
            client = pool.get_session(USER, PASSWORD)
            client.execute("SHOW SPACES;")
            client.release()
            print("  Connected!")
            pool.close()
            return True
        except Exception as e:
            print(f"  Waiting... ({e})")
            time.sleep(5)
    pool.close()
    return False


def init_schema(graphd_host, graphd_port):
    config = Config()
    config.max_connection_pool_size = 2
    pool = ConnectionPool()
    pool.init([(graphd_host, graphd_port)], config)
    client = pool.get_session(USER, PASSWORD)

    # 1. Create space
    print(f"Creating space '{SPACE}'...")
    result = client.execute(
        f"CREATE SPACE IF NOT EXISTS {SPACE} ("
        f"  vid_type=FIXED_STRING(256), "
        f"  partition_num=1, "
        f"  replica_factor=1"
        f");"
    )
    if not result.is_succeeded():
        print(f"  Error creating space: {result.error_msg()}")
    else:
        print("  Space created.")

    # Wait for space to be ready
    time.sleep(10)

    # 2. Create tags
    print("Creating tags...")
    for tag in TAGS:
        result = client.execute(f"USE {SPACE}; CREATE TAG IF NOT EXISTS {tag}("
                                f"  name STRING, "
                                f"  title STRING, "
                                f"  description STRING"
                                f");")
        if result.is_succeeded():
            print(f"  Tag: {tag} ✓")
        else:
            print(f"  Tag: {tag} ✗ ({result.error_msg()})")

    # Wait for tags
    time.sleep(5)

    # 3. Create edge types
    print("Creating edge types...")
    for edge_name, forward, description in EDGE_TYPES:
        result = client.execute(f"USE {SPACE}; CREATE EDGE IF NOT EXISTS {edge_name}("
                                f"  description STRING DEFAULT '{description}'"
                                f");")
        if result.is_succeeded():
            print(f"  Edge: {edge_name} ✓")
        else:
            print(f"  Edge: {edge_name} ✗ ({result.error_msg()})")

    client.release()
    pool.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--graphd", default=f"{GRAPH_HOST}:{GRAPH_PORT}")
    args = parser.parse_args()

    host, port = args.graphd.split(":")
    port = int(port)

    if not wait_for_graph(host, port):
        print("Timed out waiting for NebulaGraph. Is docker compose up?")
        return 1

    init_schema(host, port)
    print(f"\nSchema initialized. Space: {SPACE}, Tags: {len(TAGS)}, Edge types: {len(EDGE_TYPES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
