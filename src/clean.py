import re
import sqlite3
import unicodedata

_NON_WORD = re.compile(r"[^a-z0-9\s\-]")
_WHITESPACE = re.compile(r"\s+")


def clean_text(text) -> str:
    """Lowercase, strip punctuation and collapse whitespace. Safe on None/NaN."""
    if text is None or (isinstance(text, float) and text != text):
        return ""
    text = unicodedata.normalize("NFKC", str(text)).lower()
    text = _NON_WORD.sub(" ", text)
    return _WHITESPACE.sub(" ", text).strip()


# Terms that suggest a wearable / sensing / stimulation device
DEVICE_TERMS = [
    "wearable", "wrist", "glove", "sensor", "accelerometer", "gyroscope",
    "inertial", "actuator", "motor", "vibrat", "stimulat", "electrode",
    "stabiliz", "handheld", "utensil", "spoon", "orthosis", "exoskeleton",
    "microcontroller", "processor", "controller", "signal",
]
# Terms that suggest a drug / herbal / chemical patent
DRUG_TERMS = [
    "pharmaceutical", "medicament", "medicine", "herbal", "decoction", "extract",
    "compound", "composition", "tablet", "capsule", "formulation", "drug",
    "peptide", "antibody", "inhibitor", "agonist", "antagonist", "dosage",
]
# Human/medical context. A real tremor patent should mention at least one.
MEDICAL_TERMS = [
    "parkinson", "essential tremor", "movement disorder", "neurolog", "patient",
    "dystonia", "involuntary", "muscle", "limb", "wrist", "wearer", "hand tremor",
    "tremor of the hand", "tremor suppression", "tremor reduction",
]
MIN_SCORE = 2.0  # keep patents scoring at least this; tune after looking at samples


def relevance(title, abstract) -> float:
    text = " " + clean_text(f"{title or ''} {abstract or ''}") + " "
    if not any(t in text for t in MEDICAL_TERMS):
        return -10.0  # no human/medical context: likely mechanical "vibration" noise
    device = sum(1 for t in DEVICE_TERMS if t in text)
    drug = sum(1 for t in DRUG_TERMS if t in text)
    return device - 1.5 * drug


def main():
    from config import DB_PATH

    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT patent_id, title, abstract FROM patents").fetchall()
    con.executemany(
        "UPDATE patents SET relevance_score = ? WHERE patent_id = ?",
        [(relevance(t, a), pid) for pid, t, a in rows],
    )
    con.commit()

    kept = con.execute(
        "SELECT COUNT(*) FROM patents WHERE relevance_score >= ?", (MIN_SCORE,)
    ).fetchone()[0]
    print(f"Kept {kept} of {len(rows)} patents (score >= {MIN_SCORE})")
    print("Kept by country:", con.execute(
        "SELECT country, COUNT(*) FROM patents WHERE relevance_score >= ? "
        "GROUP BY 1 ORDER BY 2 DESC LIMIT 6", (MIN_SCORE,)).fetchall())
    print("\nSample KEPT:")
    for r in con.execute(
        "SELECT relevance_score, country, substr(title,1,70) FROM patents "
        "WHERE relevance_score >= ? ORDER BY RANDOM() LIMIT 10", (MIN_SCORE,)):
        print(r)
    print("\nSample DROPPED:")
    for r in con.execute(
        "SELECT relevance_score, country, substr(title,1,70) FROM patents "
        "WHERE relevance_score < ? ORDER BY RANDOM() LIMIT 10", (MIN_SCORE,)):
        print(r)
    con.close()


if __name__ == "__main__":
    main()