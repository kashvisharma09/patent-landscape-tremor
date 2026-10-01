import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.clean import clean_text


class PriorArtIndex:
    """TF-IDF index over patent text. Ranks patents by similarity to a query.

    df needs columns: patent_id, text, priority_date.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), sublinear_tf=True
        )
        self.matrix = self.vectorizer.fit_transform(self.df["text"].map(clean_text))

    def search(self, query: str, top_k: int = 10, before_date=None) -> pd.DataFrame:
        """Top-k most similar patents.

        before_date: only keep patents with priority_date earlier than this.
        That is the groundwork for validity/invalidity search (what existed
        before a given patent's priority date?).
        """
        q = self.vectorizer.transform([clean_text(query)])
        scores = cosine_similarity(q, self.matrix).ravel()
        result = self.df.assign(score=scores)
        if before_date is not None:
            dates = pd.to_datetime(result["priority_date"])
            result = result[dates < pd.to_datetime(before_date)]
        return result.sort_values("score", ascending=False).head(top_k)