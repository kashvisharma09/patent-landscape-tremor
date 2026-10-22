"""Run the SQL in sql/analysis_queries.sql and save tables + charts.

Usage (from the project root):
    python -m src.analysis
"""
import re
import sqlite3

import matplotlib

matplotlib.use("Agg")  # draw to files only, no pop-up windows
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

from config import DB_PATH, FIGURES_DIR, PROCESSED_DIR, ROOT
from src.clean import MIN_SCORE

QUERIES_PATH = ROOT / "sql" / "analysis_queries.sql"

COMPANY_SUFFIXES = {
    "INC", "LTD", "LLC", "CORP", "CORPORATION", "CO", "LIMITED", "GMBH", "AG",
    "SA", "BV", "PLC", "LP", "THE", "KK", "AB", "OY", "SRL", "SPA", "PTE", "PTY",
}
# Add entries here when the same organisation shows up under different spellings.
ALIASES = {
    "GREAT LAKES NEURO TECHNOLOGIES": "GREAT LAKES NEUROTECHNOLOGIES",
}


def normalize_assignee(name: str) -> str:
    text = re.sub(r"[^A-Z0-9 ]", " ", str(name).upper())
    words = [w for w in text.split() if w not in COMPANY_SUFFIXES]
    normalized = " ".join(words)
    return ALIASES.get(normalized, normalized)


def load_queries() -> dict:
    text = QUERIES_PATH.read_text(encoding="utf-8")
    parts = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.M)
    # parts = [preamble, name1, sql1, name2, sql2, ...]
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def run(con, queries, name) -> pd.DataFrame:
    return pd.read_sql_query(queries[name], con, params={"min_score": MIN_SCORE})


def save_table(df: pd.DataFrame, name: str):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)


def save_fig(fig, name: str):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=150)
    plt.close(fig)


def chart_trend(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["priority_year"], df["patents"], color="#2a6f97")
    last = int(df["priority_year"].max())
    ax.axvspan(last - 2.5, last + 0.5, color="grey", alpha=0.2)
    ax.text(last - 2.4, ax.get_ylim()[1] * 0.92, "recent filings:\nincomplete data",
            fontsize=8, va="top")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Priority year")
    ax.set_ylabel("Patent families")
    ax.set_title("Tremor-related patent families by priority year")
    save_fig(fig, "trend_by_year")


def chart_barh(labels, values, title, xlabel, name, color="#2a6f97"):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(labels[::-1], values[::-1], color=color)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    save_fig(fig, name)


def chart_country_trend(df: pd.DataFrame, top_n: int = 5):
    top = df.groupby("country")["patents"].sum().nlargest(top_n).index
    wide = (df[df["country"].isin(top)]
            .pivot_table(index="priority_year", columns="country", values="patents", fill_value=0))
    fig, ax = plt.subplots(figsize=(8, 4))
    wide.plot(ax=ax, marker="o")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Priority year")
    ax.set_ylabel("Patent families")
    ax.set_title(f"Top {top_n} patent offices over time")
    save_fig(fig, "country_trend")


def main():
    queries = load_queries()
    con = sqlite3.connect(DB_PATH)

    total = con.execute(
        "SELECT COUNT(*) FROM patents WHERE relevance_score >= ?", (MIN_SCORE,)
    ).fetchone()[0]
    if total == 0:
        raise SystemExit("No relevant patents found. Run `python -m src.clean` first.")
    print(f"Analysing {total} relevant patent families (score >= {MIN_SCORE})\n")

    trend = run(con, queries, "yearly_trend")
    save_table(trend, "yearly_trend")
    chart_trend(trend)
    print("Patents per priority year:\n", trend.to_string(index=False), "\n")

    countries = run(con, queries, "by_country")
    save_table(countries, "by_country")
    top_c = countries.head(8)
    chart_barh(list(top_c["country"]), list(top_c["patents"]),
               "Patent families by office", "Patent families", "by_country")
    print("By country:\n", countries.head(8).to_string(index=False), "\n")

    ctrend = run(con, queries, "country_trend")
    save_table(ctrend, "country_trend")
    chart_country_trend(ctrend)

    pairs = run(con, queries, "assignee_pairs")
    pairs["assignee"] = pairs["assignee_name"].map(normalize_assignee)
    assignees = (pairs.groupby("assignee")["patent_id"].nunique()
                 .sort_values(ascending=False).rename("patents").reset_index())
    save_table(assignees, "top_assignees")
    top_a = assignees.head(15)
    chart_barh(list(top_a["assignee"]), list(top_a["patents"]),
               "Top assignees (normalised names)", "Patent families", "top_assignees",
               color="#bc4749")
    print("Top assignees:\n", assignees.head(10).to_string(index=False), "\n")

    cpc = run(con, queries, "top_cpc_groups")
    save_table(cpc, "top_cpc_groups")
    if not cpc.empty:
        chart_barh(list(cpc["cpc_group"]), list(cpc["patents"]),
                   "Most common CPC main groups", "Patent families", "top_cpc_groups",
                   color="#6a994e")
        print("Top CPC groups:\n", cpc.head(10).to_string(index=False), "\n")

    grant = run(con, queries, "filing_vs_grant")
    save_table(grant, "filing_vs_grant")
    print("Share granted by priority year:\n", grant.to_string(index=False))
    print(f"\nCharts saved to {FIGURES_DIR}, tables to {PROCESSED_DIR}")
    con.close()


if __name__ == "__main__":
    main()
