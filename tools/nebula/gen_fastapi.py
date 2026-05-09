#!/usr/bin/env python3
"""
Generate FastAPI code from a NebulaGraph spec subgraph.

Usage:
    python3 gen_fastapi.py specs/auth-spec
"""

import sys
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

HOST, PORT = "127.0.0.1", 9669

def query_graph(client, spec_id):
    """Extract endpoints, contracts, requirements, and scenarios for a spec."""
    queries = {
        "endpoints": f'''
            MATCH (s:spec)-[:exposes]->(e)
            WHERE id(s) == "{spec_id}"
            RETURN id(e) AS endpoint
        ''',
        "contracts": f'''
            MATCH (s:spec)-[:exposes]->(e)-[r:accepts|:returns|:fails_with]->(c)
            WHERE id(s) == "{spec_id}"
            RETURN id(e) AS endpoint, type(r) AS predicate, id(c) AS contract
        ''',
        "requirements": f'''
            MATCH (s:spec)-[:contains]->(r:requirement)
            WHERE id(s) == "{spec_id}"
            RETURN id(r) AS requirement
        ''',
        "scenarios": f'''
            MATCH (s:spec)-[:contains]->(r:requirement)<-[:scenario_for]-(sc:scenario)
            WHERE id(s) == "{spec_id}"
            RETURN id(r) AS requirement, id(sc) AS scenario
        ''',
    }

    results = {}
    for name, query in queries.items():
        result = client.execute(query)
        results[name] = []
        if result.is_succeeded():
            for i in range(result.row_size()):
                results[name].append(result.row_values(i))
    return results


def generate_fastapi(spec_id, data):
    """Generate FastAPI route code from spec subgraph data."""

    # Extract unique endpoints
    endpoints = set()
    contracts = {}
    for row in data["endpoints"]:
        ep = row[0].as_string()
        endpoints.add(ep)
        contracts[ep] = {"accepts": [], "returns": [], "fails_with": []}

    for row in data["contracts"]:
        ep = row[0].as_string()
        pred = row[1].as_string() if hasattr(row[1], 'as_string') else str(row[1])
        contract = row[2].as_string()
        if pred in contracts.get(ep, {}):
            contracts[ep][pred].append(contract)

    # Group scenarios by requirement
    reqs = {}
    for row in data["scenarios"]:
        req = row[0].as_string()
        sc = row[1].as_string()
        reqs.setdefault(req, []).append(sc)

    # ── Generate code ──
    code = []
    code.append("# Auto-generated from NebulaGraph spec subgraph")
    code.append(f"# Spec: {spec_id}")
    code.append("")
    code.append("from fastapi import FastAPI, HTTPException")
    code.append("from pydantic import BaseModel")
    code.append("")
    code.append("app = FastAPI()")
    code.append("")

    for ep in sorted(endpoints):
        name = ep.split("/")[-1].replace("-", "_")
        ep_path = "/" + "/".join(ep.split("/")[1:]) if "/" in ep else f"/{ep}"

        # Input schema
        inputs = contracts[ep].get("accepts", [])
        input_name = inputs[0] if inputs else "Request"
        code.append(f"")
        code.append(f"class {input_name}(BaseModel):")
        code.append(f'    """Auto-generated from spec."""')
        code.append(f"    pass  # Schema from spec node: {', '.join(inputs)}")
        code.append(f"")

        # Output schema
        outputs = contracts[ep].get("returns", [])
        output_name = outputs[0] if outputs else "Response"
        code.append(f"class {output_name}(BaseModel):")
        code.append(f'    """Auto-generated from spec."""')
        code.append(f"    pass  # Schema from spec node: {', '.join(outputs)}")
        code.append(f"")

        # Error codes
        errors = contracts[ep].get("fails_with", [])
        error_map = {
            "references/http-401": (401, "Unauthorized"),
            "references/http-403": (403, "Forbidden"),
            "references/http-404": (404, "Not Found"),
            "references/http-422": (422, "Unprocessable Entity"),
            "references/http-429": (429, "Too Many Requests"),
        }

        # Route handler
        method = "post" if "post" in ep.lower() else "get"
        code.append(f"@app.{method}(\"{ep_path}\")")
        if inputs:
            code.append(f"async def {name}(body: {input_name}) -> {output_name}:")
        else:
            code.append(f"async def {name}() -> {output_name}:")

        # Docstring from requirements
        code.append(f'    """')
        for req in reqs:
            code.append(f"    Requirement: {req}")
        for sc_list in reqs.values():
            for sc in sc_list[:3]:
                code.append(f"      Scenario: {sc}")
        code.append(f'    """')

        # Error handling
        if errors:
            code.append(f"    # Contract violations generate:")
            for err in errors:
                status, msg = error_map.get(err, (500, "Internal Error"))
                code.append(f"    #   {err} → HTTP {status} ({msg})")
            code.append(f"    pass")
        else:
            code.append(f"    pass")

    return "\n".join(code)


def main():
    spec_id = sys.argv[1] if len(sys.argv) > 1 else "specs/auth-spec"

    config = Config()
    pool = ConnectionPool()
    pool.init([(HOST, PORT)], config)
    client = pool.get_session("root", "nebula")
    client.execute("USE knowledge_graph;")

    data = query_graph(client, spec_id)
    code = generate_fastapi(spec_id, data)

    print(code)

    client.release()
    pool.close()


if __name__ == "__main__":
    main()
