import re
import sqlite3

import pandas as pd

from config import DB_PATH, END_YEAR, RAW_DIR, ROOT, START_YEAR

SCHEMA_PATH = ROOT / "sql" / "schema.sql"

# Google Patents CSV header -> our column. Adjust after seeing your real file.
COLUMN_MAP = {
    "id": "patent_id",
    "title": "title",
    "assignee": "assignee",
    "inventor/author": "inventor",
    "priority date": "priority_date",
    "filing/creation date": "filing_date",
    "publication date": "publication_date",
    "grant date": "grant_date",
    "result link": "url",
}

# How multiple assignees/inventors are separated in one cell.
# Commas are NOT included because names like "Acme, Inc." would break.
SEPARATORS = re.compile(r"\s*[|;]\s*")


def read_google_patents_csv(path) -> pd.DataFrame:
    """Google's export starts with a 'search URL:' line before the real header."""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    header_idx = next(
        (i for i, line in enumerate(lines) if line.lower().startswith("id,")), 0
    )
    df = pd.read_csv(path, skiprows=header_idx, encoding="utf-8-sig")
    df.columns = [c.strip().lower() for c in df.columns]
    print(f"{path.name}: header found at line {header_idx}, columns = {list(df.columns)}")
    return df


def load_all() -> pd.DataFrame:
    frames = []
    for path in sorted(RAW_DIR.glob("*.csv")):
        df = read_google_patents_csv(path)
        df = df.rename(columns=COLUMN_MAP)
        df["source_file"] = path.name
        frames.append(df)
    if not frames:
        raise SystemExit(f"No CSV files found in {RAW_DIR}")
    df = pd.concat(frames, ignore_index=True)

    missing = [c for c in COLUMN_MAP.values() if c not in df.columns]
    if missing:
        print(f"WARNING: expected columns not found: {missing}")
        for c in missing:
            df[c] = None

    df = df.dropna(subset=["patent_id"]).drop_duplicates("patent_id")
    df["patent_id"] = df["patent_id"].str.strip()
    df["country"] = df["patent_id"].str[:2]
    for col in ["priority_date", "filing_date", "publication_date", "grant_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["priority_year"] = df["priority_date"].dt.year
    df = df[df["priority_year"].between(START_YEAR, END_YEAR)]
    return df


def explode_people(df: pd.DataFrame, col: str, out_col: str) -> pd.DataFrame:
    rows = df[["patent_id", col]].dropna()
    rows = rows.assign(**{out_col: rows[col].astype(str).str.split(SEPARATORS)})
    rows = rows.explode(out_col)
    rows[out_col] = rows[out_col].str.strip()
    return rows[rows[out_col] != ""][["patent_id", out_col]].drop_duplicates()


def main():
    df = load_all()
    DB_PATH.parent.mkdir(exist_ok=True)

    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    patent_cols = [
        "patent_id", "country", "title", "priority_date", "filing_date",
        "publication_date", "grant_date", "priority_year", "url", "source_file",
    ]
    out = df[patent_cols].copy()
    for col in ["priority_date", "filing_date", "publication_date", "grant_date"]:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_sql("patents", con, if_exists="append", index=False)

    explode_people(df, "assignee", "assignee_name").to_sql(
        "patent_assignees", con, if_exists="append", index=False
    )
    explode_people(df, "inventor", "inventor_name").to_sql(
        "patent_inventors", con, if_exists="append", index=False
    )
    con.commit()

    for table in ["patents", "patent_assignees", "patent_inventors"]:
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {n} rows")
    print("Sample assignees:", [r[0] for r in con.execute(
        "SELECT assignee_name FROM patent_assignees LIMIT 8")])
    con.close()


if __name__ == "__main__":
    main()