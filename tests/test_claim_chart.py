from src.analysis import normalize_assignee
from src.claim_chart import ELEMENTS, build_chart, map_elements


def test_map_elements_finds_features():
    text = ("A wrist-worn device with an accelerometer and a microcontroller performing an FFT "
            "and driving an actuator in closed-loop feedback.")
    found = map_elements(text)
    assert found["Wrist-worn / wearable form factor"] == "wrist"
    assert found["Inertial sensing (IMU / accelerometer / gyroscope)"] == "accelerometer"
    assert found["Digital signal processing (FFT / filtering)"] == "fft"
    assert found["Machine-learning / adaptive personalisation"] is None


def test_build_chart_has_one_row_per_element():
    rows = [{"patent_id": "US1", "url": "u", "priority_date": "2015-01-01", "assignee": "Acme",
             "score": 0.5, "title": "Wearable tremor device", "abstract": "A wearable accelerometer."}]
    chart = build_chart(rows)
    for element in ELEMENTS:
        assert element in chart
    assert "Screening only" in chart


def test_normalize_assignee_merges_spelling_variants():
    assert normalize_assignee("Cala Health, Inc.") == normalize_assignee("CALA HEALTH INC")
    assert normalize_assignee("Great Lakes Neuro Technologies Inc.") == "GREAT LAKES NEUROTECHNOLOGIES"
