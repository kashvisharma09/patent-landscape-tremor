"""Feature-by-feature comparison of your device against the closest prior art.

This is an ABSTRACT-LEVEL screening chart. Our data has titles and abstracts, not
claim text, so "Yes" means the abstract mentions the feature, not that a claim
covers it. Read the full claims of the top results on Google Patents before
drawing any conclusion about infringement or novelty.

Usage (from the project root):
    python -m src.claim_chart            # chart for MY_INVENTION vs the top 3 results
    python -m src.claim_chart --top 5
"""
import argparse
import sqlite3

from config import DB_PATH, MY_INVENTION, ROOT
from src.clean import clean_text
from src.run_prior_art import build_index

# Elements of the invention and the words that suggest the abstract discloses them.
ELEMENTS = {
    "Wrist-worn / wearable form factor": ["wrist", "wearable", "worn", "glove", "wristband", "bracelet"],
    "Inertial sensing (IMU / accelerometer / gyroscope)": ["inertial", "imu", "accelerometer", "gyroscope"],
    "Tremor detection in a frequency band (about 4-12 Hz)": ["frequency", " hz", "oscillat", "spectrum", "spectral"],
    "Digital signal processing (FFT / filtering)": ["fft", "fourier", "filter", "bandpass", "band-pass"],
    "Microcontroller / processor": ["microcontroller", "processor", "controller", "processing unit"],
    "Actuator applying counter-phase / opposing motion": ["actuator", "servo", "counter", "opposing", "cancel", "damping", "suppress"],
    "Closed-loop feedback": ["closed-loop", "closed loop", "feedback"],
    "Machine-learning / adaptive personalisation": ["machine learning", "neural", "classifier", "adaptive", "learning", "personali"],
}


def map_elements(text: str) -> dict:
    """For each element, return the first matching keyword in the text, or None."""
    t = " " + clean_text(text) + " "
    result = {}
    for element, keywords in ELEMENTS.items():
        hit = next((k for k in keywords if k in t), None)
        result[element] = hit.strip() if hit else None
    return result


def build_chart(rows) -> str:
    ids = [r["patent_id"] for r in rows]
    maps = [map_elements(f"{r['title']}. {r['abstract']}") for r in rows]

    lines = ["# Abstract-level claim chart: my device vs closest prior art", ""]
    lines += ["**My device:** " + MY_INVENTION, ""]
    lines += ["> Screening only. \"Yes\" means the abstract mentions the feature; it does not mean a claim "
              "covers it. Read the full claims of each patent before drawing conclusions.", ""]
    lines += ["| # | Patent | Priority | Assignee | Similarity | Title |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, start=1):
        lines.append(f"| {i} | [{r['patent_id']}]({r['url']}) | {r['priority_date']} | "
                     f"{str(r['assignee'])[:40]} | {r['score']:.2f} | {str(r['title'])[:70]} |")
    lines += ["", "| Element of my device | " + " | ".join(f"#{i}" for i in range(1, len(rows) + 1)) + " |",
              "|---|" + "---|" * len(rows)]
    for element in ELEMENTS:
        cells = [f"Yes ({m[element]})" if m[element] else "No" for m in maps]
        lines.append(f"| {element} | " + " | ".join(cells) + " |")
    coverage = [sum(1 for v in m.values() if v) for m in maps]
    lines += ["", "**Elements found in abstract:** " + ", ".join(
        f"#{i} {ids[i - 1]}: {c}/{len(ELEMENTS)}" for i, c in enumerate(coverage, start=1)), ""]
    lines += ["**Where my device may differ:** elements marked \"No\" across all columns are candidates "
              "for what is distinctive. Confirm by reading the full text, then write the differences "
              "into the draft specification and claims.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--top", type=int, default=3)
    args = parser.parse_args()

    con = sqlite3.connect(DB_PATH)
    index = build_index(con)
    results = index.search(MY_INVENTION, top_k=args.top)
    rows = results.to_dict("records")
    chart = build_chart(rows)

    out = ROOT / "reports" / "claim_chart.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(chart, encoding="utf-8")
    for r, m in zip(rows, (map_elements(f"{r['title']}. {r['abstract']}") for r in rows)):
        found = sum(1 for v in m.values() if v)
        print(f"{r['patent_id']}  {found}/{len(ELEMENTS)} elements  {str(r['title'])[:60]}")
    print(f"\nSaved {out}")
    con.close()


if __name__ == "__main__":
    main()
