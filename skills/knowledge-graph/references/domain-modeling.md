# Domain Modeling with the Knowledge Graph

How to build a rich, queryable subgraph for a domain — drawn from building the 66-node Vedanta lineage graph.

## The Pattern

Every domain model follows the same 4-phase approach:

### Phase 1: Identify the entity kinds

Before ingesting, list what TYPES of nodes the domain needs:

```
People:       key figures, teachers, students, authors
Concepts:     ideas, philosophies, techniques, frameworks
References:   texts, events, sources, documents  
Organizations: groups, institutions, movements
```

Each kind maps to a directory. Always use plural: `people/`, `concepts/`, `references/`, `organizations/`.

### Phase 2: Choose the spine predicate

Every domain has one primary relationship that forms its backbone:

```
Vedanta lineage:    teaches / taught_by     (guru → shishya)
Upanishadic corpus: portion_of / contains    (text → parent collection)
REIT analysis:      produces / produced_by   (project → output)
Options toolkit:    uses / used_by           (project → tool)
```

Build the spine FIRST — all other edges hang off it.

### Phase 3: Layer secondary predicates

After the spine, add the cross-cutting relationships:

```
Temporal:     precedes / succeeds           (chronological ordering)
Belief:       attests / attested_by          (what a source confirms)
Dependency:   influences / influenced_by     (how ideas flow)
Organization: associated_with               (institutional membership)
```

### Phase 4: The payoff query

Every domain model should have one "hero query" that demonstrates the graph's power:

```
Vedanta:  python3 query.py --path "sri-ramakrishna" "koustubh"
          → 2 hops across 150 years of transmission
          
REIT:     python3 query.py "reit-analyzer" --depth 3
          → full ecosystem of REITs, metrics, precedents

Upanishads: python3 query.py "upanishads" --depth 2
          → all 11 texts, their Vedas, their concepts
```

## Rules

1. **Spine first, details later.** If you can't trace the main path in 2-3 hops, the spine is wrong.
2. **One node per entity.** Sri Ramakrishna is one node, not separate nodes for "Ramakrishna the mystic" and "Ramakrishna the teacher."
3. **Minimal viable predicates.** Start with 3-4 predicate types. Add more only when a query demands it.
4. **The hero query is the acceptance test.** If it doesn't return something surprising and useful, the model is too shallow.
5. **Lint after every bulk ingest.** 11 Upanishads × 3 edges each = 33 edges. One broken reverse edge poisons the graph.

## Anti-Patterns

- **Flat star schema.** If every node only connects to one central hub, you have a directory, not a graph.
- **Over-modeling.** Not every character needs a node. The 16 disciples of Ramakrishna don't all need nodes unless they form queryable relationships.
- **Singular kinds.** The frontmatter `kind:` field should be singular (`person`, `concept`), the directory should be plural (`people/`, `concepts/`). The ingest script derives the edge path from the directory, not the frontmatter kind field.
