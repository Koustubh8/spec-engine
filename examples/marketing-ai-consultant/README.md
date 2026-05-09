# Marketing AI Consultant

A self-improving ML-powered marketing analytics consultant. Spec'd in the knowledge graph but not yet built.

## Spec Graph

The full spec is in `knowledge-graph/specs/`:

| Spec | Description | Requirements |
|------|-------------|-------------|
| `mmm-spec` | Bayesian Marketing Mix Modeling with PyMC | 5 |
| `clv-spec` | Predictive Customer Lifetime Value with XGBoost | 5 |
| `uplift-spec` | Causal inference for campaign treatment effects | 5 |
| `segmentation-spec` | RFM + behavioral clustering with drift monitoring | 5 |
| `creative-spec` | Bayesian A/B testing + creative fatigue detection | 5 |
| `self-improvement-spec` | MLflow + DSPy optimization + NebulaGraph lineage | 5 |
| `consultant-interface-spec` | React chat + NLP query routing | 5 |
| `data-ingestion-spec` | Streaming/batch pipeline with schema-on-read | 4 |

## How to Query

```bash
cd tools/knowledge-graph
python3 query.py "mktg-ai-platform" --depth 2
python3 query.py --path "mmm-spec" "uplift-spec"
```

## Status

📋 Spec complete — ready for implementation.
