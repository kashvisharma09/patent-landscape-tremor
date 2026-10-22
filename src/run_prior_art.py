"""Prior-art / novelty and validity searches over the relevant patents.

Usage (from the project root):
    python -m src.run_prior_art                          # novelty search for MY_INVENTION
    python -m src.run_prior_art --query "your text"      # novelty search for any description
    python -m src.run_prior_art --validity US12453853B2  # what existed BEFORE this patent's priority date?
"""
import argparse
import sqlite3

import pandas as pd

from config import DB_PATH, MY_INVENTION, ROOT, TOP_K
from src.clean import MIN_SCORE
from src.prior_art import PriorArtIndex

REPORTS = ROOT / "reports"
CORPUS_SQL = """
SELECT p.patent_id, p.country, p.title, p.abstract, p.priority_date, p.url,
       (SELECT group_concat(assignee_name, ' | ')
          FROM patent_assignees a WHERE a.patent_id = p.patent_id) AS assignee
FROM patents p
"""


def load_corpus(con) -> pd.DataFrame:
    df = pd.read_sql_query(CORPUS_SQL + " WHERE p.relevance_score >= ?", con,
                           params=(MIN_SCORE,))
    df["text"] = df["title"].fillna("") + ". " + df["abstract"].fillna("")
    return df


def build_index(con) -> PriorArtIndex:
    df = load_corpus(con)
    if df.empty:
        raise SystemExit("No relevant patents in the database. Run ingest and clean first.")
    return PriorArtIndex(df)


def show(results: pd.DataFrame):
    for rank, (_, r) in enumerate(results.iterrows(), start=1):
        print(f"{rank:>2}. {r['score']:.3f}  {r['patent_id']}  ({r['priority_date']})  "
              f"{str(r['title'])[:80]}")
        print(f"      {str(r['assignee'])[:70]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--query", help="invention description (default: MY_INVENTION in config.py)")
    parser.add_argument("--validity", metavar="PATENT_ID",
                        help="find earlier patents that could challenge this one")
    parser.add_argument("--top", type=int, default=TOP_K)
    args = parser.parse_args()

    con = sqlite3.connect(DB_PATH)
    index = build_index(con)
    REPORTS.mkdir(parents=True, exist_ok=True)

    if args.validity:
        row = con.execute(
            "SELECT patent_id, title, abstract, priority_date FROM patents WHERE patent_id = ?",
            (args.validity,)).fetchone()
        if row is None:
            raise SystemExit(f"{args.validity} is not in the database.")
        pid, title, abstract, priority = row
        if not priority:
            raise SystemExit(f"{pid} has no priority date, so a validity cut-off is not possible.")
        query = f"{title or ''}. {abstract or ''}"
        results = index.search(query, top_k=args.top + 1, before_date=priority)
        results = results[results["patent_id"] != pid].head(args.top)
        print(f"Validity search for {pid} ({title})\nOnly patents with priority before {priority}:\n")
        out = REPORTS / f"validity_{pid}.csv"
    else:
        query = args.query or MY_INVENTION
        results = index.search(query, top_k=args.top)
        print("Novelty / prior-art search\nQuery:", query[:200], "\n")
        out = REPORTS / "prior_art_top10.csv"

    show(results)
    results.drop(columns=["text"], errors="ignore").to_csv(out, index=False)
    print(f"\nSaved {out}")
    con.close()


if __name__ == "__main__":
    main()
