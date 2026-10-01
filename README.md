# Patent Landscape: Wearable Tremor Suppression

A Python + SQL pipeline for patent landscape analysis, prior-art search, and claim charting, focused on wearable tremor suppression devices.

**Status:** work in progress

## Planned features
- Landscape analysis (filing trends, top assignees, technology clusters)
- Prior-art / novelty search (TF-IDF similarity ranking)
- Validity search (date-cutoff mode)
- Claim chart and draft specification

## Setup
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -v
```

## Project structure
- `src/` - ingestion, cleaning, clustering, prior-art search, claim chart
- `sql/` - database schema and analysis queries
- `tests/` - unit tests
- `notebooks/` - exploration and results
- `reports/` - figures and draft specification