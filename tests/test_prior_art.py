import pandas as pd
from src.prior_art import PriorArtIndex

TOY = pd.DataFrame(
    {
        "patent_id": ["US1", "US2", "US3", "US4"],
        "text": [
            "Wrist worn device with inertial sensor and actuator to suppress hand tremor",
            "Deep brain stimulation electrode for treating parkinson disease",
            "Method for baking sourdough bread with controlled fermentation",
            "Gas sensor for detecting acetone in exhaled breath",
        ],
        "priority_date": ["2012-03-01", "2008-06-15", "2015-01-10", "2019-09-30"],
    }
)

QUERY = "wearable tremor suppression using an inertial sensor and actuator"


def test_most_relevant_patent_ranks_first():
    top = PriorArtIndex(TOY).search(QUERY, top_k=3)
    assert top.iloc[0]["patent_id"] == "US1"


def test_top_k_limits_results():
    assert len(PriorArtIndex(TOY).search(QUERY, top_k=2)) == 2


def test_before_date_excludes_later_patents():
    top = PriorArtIndex(TOY).search(QUERY, top_k=10, before_date="2010-01-01")
    assert list(top["patent_id"]) == ["US2"]