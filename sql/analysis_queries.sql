-- Landscape analysis queries.
-- Each block starts with "-- name: <query_name>" and is run by src/analysis.py.
-- :min_score is the relevance cut-off (see MIN_SCORE in src/clean.py).

-- name: yearly_trend
-- Patent families per priority year (the year the idea first appeared).
SELECT priority_year, COUNT(*) AS patents
FROM patents
WHERE relevance_score >= :min_score
  AND priority_year IS NOT NULL
GROUP BY priority_year
ORDER BY priority_year;

-- name: by_country
-- Where the patent offices are. Country is the office of the representative family member.
SELECT country, COUNT(*) AS patents
FROM patents
WHERE relevance_score >= :min_score
GROUP BY country
ORDER BY patents DESC;

-- name: country_trend
-- Patents per priority year for each country (analysis.py keeps the top few).
SELECT priority_year, country, COUNT(*) AS patents
FROM patents
WHERE relevance_score >= :min_score
  AND priority_year IS NOT NULL
GROUP BY priority_year, country
ORDER BY priority_year;

-- name: assignee_pairs
-- Raw patent/assignee pairs. Names are normalised in Python (case, "Inc." etc.) and then counted.
SELECT a.patent_id, a.assignee_name, p.priority_year
FROM patent_assignees a
JOIN patents p ON p.patent_id = a.patent_id
WHERE p.relevance_score >= :min_score;

-- name: top_cpc_groups
-- Most common CPC main groups (e.g. A61B5 = measuring for diagnostic purposes).
SELECT
    CASE WHEN instr(c.cpc_code, '/') > 0
         THEN substr(c.cpc_code, 1, instr(c.cpc_code, '/') - 1)
         ELSE c.cpc_code END AS cpc_group,
    COUNT(DISTINCT c.patent_id) AS patents
FROM patent_cpc c
JOIN patents p ON p.patent_id = c.patent_id
WHERE p.relevance_score >= :min_score
GROUP BY cpc_group
ORDER BY patents DESC
LIMIT 15;

-- name: filing_vs_grant
-- Share of relevant families that are already granted, per priority year.
-- Explains why recent years look thin: newer filings have not been granted yet.
SELECT priority_year,
       COUNT(*) AS patents,
       ROUND(100.0 * SUM(CASE WHEN grant_date IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_granted
FROM patents
WHERE relevance_score >= :min_score
  AND priority_year IS NOT NULL
GROUP BY priority_year
ORDER BY priority_year;
