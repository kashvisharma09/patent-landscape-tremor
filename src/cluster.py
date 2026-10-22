"""Cluster the relevant patents into technology sub-areas (TF-IDF + KMeans).

Usage (from the project root):
    python -m src.cluster
Writes cluster_id into the patents table, plus reports/cluster_summary.csv
and reports/figures/clusters.png.
"""
import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from config import DB_PATH, FIGURES_DIR, ROOT
from src.analysis import normalize_assignee
from src.clean import MIN_SCORE, clean_text

K_RANGE = range(4, 11)
SEED = 42


def load_relevant(con) -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT patent_id, country, title, abstract, priority_year FROM patents "
        "WHERE relevance_score >= ?", con, params=(MIN_SCORE,))
    df["text"] = (df["title"].fillna("") + ". " + df["abstract"].fillna("")).map(clean_text)
    return df[df["text"].str.len() > 0].reset_index(drop=True)


def choose_k(matrix, n_docs: int):
    """Pick k by silhouette score. Returns (best_k, {k: score})."""
    scores = {}
    for k in K_RANGE:
        if k >= n_docs:
            break
        labels = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit_predict(matrix)
        if len(set(labels)) < 2:
            continue
        scores[k] = silhouette_score(matrix, labels, metric="cosine")
    if not scores:
        raise SystemExit("Not enough patents to cluster.")
    return max(scores, key=scores.get), scores


def top_terms(model, vectorizer, n: int = 6):
    terms = np.array(vectorizer.get_feature_names_out())
    order = model.cluster_centers_.argsort(axis=1)[:, ::-1]
    return [list(terms[row[:n]]) for row in order]


def main():
    con = sqlite3.connect(DB_PATH)
    df = load_relevant(con)
    if len(df) < 12:
        raise SystemExit(f"Only {len(df)} relevant patents: too few to cluster. "
                         "Run `python -m src.clean` or load more data.")
    print(f"Clustering {len(df)} patents")

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                 min_df=2, max_df=0.5, sublinear_tf=True)
    matrix = vectorizer.fit_transform(df["text"])

    best_k, scores = choose_k(matrix, len(df))
    print("Silhouette by k:", {k: round(v, 3) for k, v in scores.items()})
    print("Chosen k =", best_k)

    model = KMeans(n_clusters=best_k, n_init=10, random_state=SEED).fit(matrix)
    df["cluster_id"] = model.labels_
    terms = top_terms(model, vectorizer)

    con.execute("UPDATE patents SET cluster_id = NULL")
    con.executemany("UPDATE patents SET cluster_id = ? WHERE patent_id = ?",
                    [(int(c), pid) for c, pid in zip(df["cluster_id"], df["patent_id"])])
    con.commit()

    assignees = pd.read_sql_query("SELECT patent_id, assignee_name FROM patent_assignees", con)
    assignees["assignee"] = assignees["assignee_name"].map(normalize_assignee)
    df = df.merge(assignees[["patent_id", "assignee"]], on="patent_id", how="left")

    rows = []
    for c in range(best_k):
        sub = df[df["cluster_id"] == c]
        uniq = sub.drop_duplicates("patent_id")
        rows.append({
            "cluster_id": c,
            "label": ", ".join(terms[c][:3]),
            "patents": len(uniq),
            "median_priority_year": float(uniq["priority_year"].median()),
            "top_countries": ", ".join(f"{k} ({v})" for k, v in
                                       uniq["country"].value_counts().head(3).items()),
            "top_assignees": ", ".join(f"{k} ({v})" for k, v in
                                       sub.dropna(subset=["assignee"])
                                       .groupby("assignee")["patent_id"].nunique()
                                       .nlargest(3).items()),
            "top_terms": ", ".join(terms[c]),
        })
    summary = pd.DataFrame(rows).sort_values("patents", ascending=False)
    out_path = ROOT / "reports" / "cluster_summary.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_path, index=False)
    print("\n" + summary[["cluster_id", "label", "patents", "median_priority_year",
                          "top_countries"]].to_string(index=False))

    # 2-D picture of the clusters
    uniq = df.drop_duplicates("patent_id").reset_index(drop=True)
    xy = TruncatedSVD(n_components=2, random_state=SEED).fit_transform(
        vectorizer.transform(uniq["text"]))
    fig, ax = plt.subplots(figsize=(9, 6))
    cmap = plt.get_cmap("tab10")
    for c in range(best_k):
        mask = uniq["cluster_id"] == c
        ax.scatter(xy[mask, 0], xy[mask, 1], s=14, color=cmap(c % 10), alpha=0.7,
                   label=f"{c}: {', '.join(terms[c][:3])}")
    ax.set_title("Technology clusters (TF-IDF, projected to 2-D)")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(fontsize=7, loc="best")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "clusters.png", dpi=150)
    plt.close(fig)
    print(f"\nSaved {out_path} and {FIGURES_DIR / 'clusters.png'}")
    con.close()


if __name__ == "__main__":
    main()
