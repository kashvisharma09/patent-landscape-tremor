-- Patent landscape: tremor suppression
-- One row per patent family representative

DROP TABLE IF EXISTS patent_assignees;
DROP TABLE IF EXISTS patent_inventors;
DROP TABLE IF EXISTS patent_cpc;
DROP TABLE IF EXISTS patent_citations;
DROP TABLE IF EXISTS patents;

CREATE TABLE patents (
    patent_id        TEXT PRIMARY KEY,
    country          TEXT,
    title            TEXT,
    abstract         TEXT,
    priority_date    DATE,
    filing_date      DATE,
    publication_date DATE,
    grant_date       DATE,
    priority_year    INTEGER,
    url              TEXT,
    source_file      TEXT,
    relevance_score  REAL,
    cluster_id       INTEGER
);

CREATE TABLE patent_assignees (
    patent_id     TEXT NOT NULL REFERENCES patents(patent_id),
    assignee_name TEXT NOT NULL,
    PRIMARY KEY (patent_id, assignee_name)
);

CREATE TABLE patent_inventors (
    patent_id     TEXT NOT NULL REFERENCES patents(patent_id),
    inventor_name TEXT NOT NULL,
    PRIMARY KEY (patent_id, inventor_name)
);

CREATE TABLE patent_cpc (
    patent_id TEXT NOT NULL REFERENCES patents(patent_id),
    cpc_code  TEXT NOT NULL,
    PRIMARY KEY (patent_id, cpc_code)
);

CREATE TABLE patent_citations (
    patent_id       TEXT NOT NULL REFERENCES patents(patent_id),
    cited_patent_id TEXT NOT NULL,
    PRIMARY KEY (patent_id, cited_patent_id)
);

CREATE INDEX idx_patents_priority_year ON patents(priority_year);
CREATE INDEX idx_patents_country ON patents(country);
CREATE INDEX idx_assignees_name ON patent_assignees(assignee_name);