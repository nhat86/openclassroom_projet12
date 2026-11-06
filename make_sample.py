import pandas as pd

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
data = pd.read_csv("dataset.csv")
data["Tag_merged"] = data["Tag"].replace(TAG_MAPPING)
data_ml = data.dropna(subset=["Consumer Claim", "Tag_merged"])

sample = data_ml.groupby("Tag_merged", group_keys=False).apply(
    lambda g: g.sample(frac=0.15, random_state=42)
)
sample.to_csv("dataset_sample.csv", index=False)