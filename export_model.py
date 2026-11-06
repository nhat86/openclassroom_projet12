import json
import time
from datetime import datetime, timezone

import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATASET_PATH = "dataset_sample.csv"

TAG_MAPPING = {
    "Credit reporting": "Credit reporting, credit repair services, or other personal consumer reports",
    "Credit card": "Credit card or prepaid card",
    "Prepaid card": "Credit card or prepaid card",
    "Bank account or service": "Checking or savings account",
    "Payday loan": "Payday loan, title loan, or personal loan",
    "Money transfers": "Money transfer, virtual currency, or money service",
    "Virtual currency": "Money transfer, virtual currency, or money service",
    "Other financial service": "Money transfer, virtual currency, or money service",
    "Consumer Loan": "Vehicle loan or lease",
    "Payday Loan": "Payday loan, title loan, or personal loan",
}


def main():
    data = pd.read_csv(DATASET_PATH)
    data["Tag_merged"] = data["Tag"].replace(TAG_MAPPING)

    
    data_ml = data.dropna(subset=["Consumer Claim", "Tag_merged"]).copy()
    data_ml["Consumer Claim"] = data_ml["Consumer Claim"].str.strip()
    data_ml["Tag_merged"] = data_ml["Tag_merged"].str.strip()
    data_ml = data_ml[
        (data_ml["Consumer Claim"] != "") & (data_ml["Tag_merged"] != "")
    ]

    X = data_ml["Consumer Claim"]
    y = data_ml["Tag_merged"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            min_df=2,
            max_features=20000,
            sublinear_tf=True,
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
        )),
    ])

    start = time.perf_counter()
    model.fit(X_train, y_train)
    training_time = time.perf_counter() - start

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    metrics = {
        "model": "TfidfVectorizer + LogisticRegression",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "dataset": DATASET_PATH,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "f1_weighted": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        "training_seconds": training_time,
        "per_class": report,
    }
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Exported model.pkl and metrics.json")


if __name__ == "__main__":
    main()