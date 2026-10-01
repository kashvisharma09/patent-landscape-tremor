from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = ROOT / "db" / "patents.db"
FIGURES_DIR = ROOT / "reports" / "figures"

# Niche: wearable tremor suppression
KEYWORDS = [
    "tremor", "parkinson", "essential tremor",
    "tremor suppression", "tremor stabilization",
    "involuntary movement", "hand stabiliz",
]

# CPC codes to filter on (starting guesses; we'll verify against real data)
CPC_PREFIXES = [
    "A61B5/1101",  # detecting tremor
    "A61B5/4082",  # movement disorders (Parkinson's etc.)
    "A61N1/36",    # electrotherapy / stimulation
    "A61H",        # physical therapy apparatus
]

# Date range
START_YEAR = 2005
END_YEAR = 2026

# Your own invention, used by the prior-art search
MY_INVENTION = (
    "A wrist-worn closed-loop device using a 6-axis inertial measurement unit "
    "to capture tremor oscillations at 4 to 12 Hz, a microcontroller applying "
    "FFT and digital filtering to isolate the tremor signal, and a servo "
    "actuator driven by PWM to apply counter-phase motion for suppression, "
    "with an adaptive machine learning classifier for low-latency personalization."
)

TOP_K = 10