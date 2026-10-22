# Patent Landscape: Wearable Tremor Suppression

A Python + SQL pipeline that builds a patent landscape for wearable tremor suppression, runs
prior-art (novelty) and validity searches, and produces a feature-by-feature comparison and a
practice patent specification for my own device (a wrist-worn, IMU-based, counter-phase
actuation tremor suppressor).

I chose this niche because I am building the device myself, so I can judge the technical
content of the patents rather than only counting them.

## What it does

| Patent-analyst task | Where it lives |
|---|---|
| Landscape analysis (trends, assignees, offices, CPC classes) | `sql/analysis_queries.sql`, `src/analysis.py` |
| Technology clustering | `src/cluster.py` (TF-IDF + KMeans, k chosen by silhouette score) |
| Prior-art / novelty search | `src/prior_art.py`, `src/run_prior_art.py` |
| Validity search (what existed before a given patent's priority date) | `python -m src.run_prior_art --validity <patent id>` |
| Infringement-style feature comparison | `src/claim_chart.py` (abstract-level screening) |
| Drafting a specification and claims | `reports/draft_specification.md` |

## Data

- Source: Google Patents Public Data on BigQuery (`patents-public-data.patents.publications`),
  queried with SQL. Worldwide publications (grants and applications), priority years 2005 to 2025.
- Selection: tremor / Parkinson / dyskinesia / involuntary movement as whole words in the title or
  abstract, **and** at least one CPC class in A61, G16H, A47G, A63B, B25J or G01P.
- One row per patent family. Raw CSVs are not committed (`data/raw/` is git-ignored).
- A relevance score (`src/clean.py`) then removes drug/herbal patents and machine-translation
  noise: the first, looser query returned many Chinese utility models in which words like
  "vibration" appeared to be translated as "tremor". Only patents scoring at least
  `MIN_SCORE` are analysed.

## Results

> Fill these in after running the pipeline, using the numbers and charts it produces.

- Dataset: **<N>** patent families after filtering (<N_raw> before the relevance filter).
- Trend: see `reports/figures/trend_by_year.png`. **<one sentence on the trend>**
- Leading assignees: see `reports/figures/top_assignees.png`. **<top 3 and what they work on>**
- Offices: see `reports/figures/by_country.png`. **<one sentence>**
- Technology clusters: see `reports/cluster_summary.csv` and `reports/figures/clusters.png`.
  **<name each cluster, e.g. stimulation, monitoring, wearable actuation, utensils>**
- Closest prior art to my device: see `reports/prior_art_top10.csv` and `reports/claim_chart.md`.
  **<top 3 patents and which elements of my device they do or do not mention>**

## How to run

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 1. put the BigQuery export in data/raw/ (see "Data"), then:
python -m src.ingest        # load CSV into SQLite (db/patents.db)
python -m src.clean         # relevance score
python -m src.analysis      # tables + charts
python -m src.cluster       # technology clusters
python -m src.run_prior_art # novelty search for my device
python -m src.claim_chart   # feature comparison vs top results
python -m pytest -v         # tests
```

## Limitations

- **Abstract-level only.** The data has titles and abstracts, not claims. The prior-art ranking is
  TF-IDF text similarity and the claim chart only shows whether an abstract mentions a feature.
  Neither is a freedom-to-operate or infringement opinion; real claims must be read in full.
- **Keyword relevance filter.** `src/clean.py` is a simple word-list score. It removes obvious
  noise but will miss some relevant patents and keep some irrelevant ones.
- **Recent years are incomplete.** Applications filed in the last two to three years are often not yet
  published or granted, so the newest bars understate activity (the chart shades them).
- **Assignee names** are normalised by rules plus a small alias table in `src/analysis.py`;
  individuals filing in their own names are not merged with their companies.
- **English text only.** Patents without an English title or abstract are not matched.

## Project structure

- `src/` ingestion, cleaning, analysis, clustering, prior-art search, claim chart
- `sql/` schema and analysis queries
- `tests/` unit tests
- `reports/` figures, cluster summary, prior-art results, claim chart, draft specification
