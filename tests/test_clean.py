from src.clean import MIN_SCORE, clean_text, relevance


def test_clean_text_handles_none_and_punctuation():
    assert clean_text(None) == ""
    assert clean_text(float("nan")) == ""
    assert clean_text("  Hello,   WORLD!  ") == "hello world"


def test_wearable_tremor_patent_is_relevant():
    score = relevance(
        "Wrist-worn tremor suppression device",
        "A wearable device for patients with Parkinson's disease has an accelerometer, "
        "a processor and an actuator that applies a counter motion to the wrist.",
    )
    assert score >= MIN_SCORE


def test_mechanical_noise_is_rejected():
    assert relevance("A kind of tower crane base", "Reduces tremor of the crane foundation") < MIN_SCORE


def test_drug_patent_is_rejected():
    score = relevance(
        "Pharmaceutical composition for Parkinson's disease",
        "A compound, tablet and capsule formulation for treating patients with tremor.",
    )
    assert score < MIN_SCORE
