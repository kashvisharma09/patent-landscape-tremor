import re
import sqlite3

import pandas as pd

from config import DB_PATH, END_YEAR, RAW_DIR, ROOT, START_YEAR

SCHEMA_PATH = ROOT / "sql" / "schema.sql"
SEP = re.compile(r"\s*\|\s*")
DATE_COLS = ["priority_date", "filing_date", "publication_date", "grant_date"]
REQUIRED = [
    "publication_number", "family_id", "title", "abstract", "assignee",
    "inventor", "cpc_codes",
] + DATE_COLS


def to_date(series: pd.Series) -> pd.Series:
    """BigQuery dates are numbers like 20130121; 0 or blank means unknown."""
    text = series.astype(str).str.replace(r"\.0$", "", regex=True)
    return pd.to_datetime(text, format="%Y%m%d", errors="coerce")


def load_all() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise SystemExit(f"No CSV files found in {RAW_DIR}")
    frames = []
    for path in files:
        df = pd.read_csv(path, encoding="utf-8-sig")
        df.columns = [c.strip().lower() for c in df.columns]
        df["source_file"] = path.name
        print(f"{path.name}: {len(df)} rows, columns = {list(df.columns)}")
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing expected columns: {missing}")

    df["patent_id"] = df["publication_number"].astype(str).str.replace("-", "", regex=False).str.strip()
    df["country"] = df["patent_id"].str[:2]
    for col in DATE_COLS:
        df[col] = to_date(df[col])
    df["priority_year"] = df["priority_date"].dt.year
    df["url"] = "https://patents.google.com/patent/" + df["patent_id"]

    df = df.drop_duplicates("patent_id")
    # One row per patent family: keep the earliest grant. Family id <= 0 means unknown.
    fam = pd.to_numeric(df["family_id"], errors="coerce")
    df["family_key"] = fam.where(fam > 0).astype("Int64").astype(str)
    df.loc[fam.isna() | (fam <= 0), "family_key"] = df["patent_id"]
    df = df.sort_values("grant_date").drop_duplicates("family_key")

    df = df[df["priority_year"].between(START_YEAR, END_YEAR)]
    return df.reset_index(drop=True)


def explode_list(df: pd.DataFrame, col: str, out_col: str) -> pd.DataFrame:
    rows = df[["patent_id", col]].dropna()
    rows = rows.assign(**{out_col: rows[col].astype(str).str.split(SEP)})
    rows = rows.explode(out_col)
    rows[out_col] = rows[out_col].str.strip()
    return rows[rows[out_col] != ""][["patent_id", out_col]].drop_duplicates()


def main():
    df = load_all()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    patent_cols = [
        "patent_id", "country", "title", "abstract", "priority_date", "filing_date",
        "publication_date", "grant_date", "priority_year", "url", "source_file",
    ]
    out = df[patent_cols].copy()
    for col in DATE_COLS:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_sql("patents", con, if_exists="append", index=False)

    explode_list(df, "assignee", "assignee_name").to_sql(
        "patent_assignees", con, if_exists="append", index=False)
    explode_list(df, "inventor", "inventor_name").to_sql(
        "patent_inventors", con, if_exists="append", index=False)
    explode_list(df, "cpc_codes", "cpc_code").to_sql(
        "patent_cpc", con, if_exists="append", index=False)
    con.commit()

    for table in ["patents", "patent_assignees", "patent_inventors", "patent_cpc"]:
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {n} rows")
    print("By country:", con.execute(
        "SELECT country, COUNT(*) FROM patents GROUP BY country ORDER BY 2 DESC LIMIT 6").fetchall())
    print("Top assignees:", con.execute(
        "SELECT assignee_name, COUNT(*) FROM patent_assignees GROUP BY 1 ORDER BY 2 DESC LIMIT 5").fetchall())
    con.close()


if __name__ == "__main__":
    main()