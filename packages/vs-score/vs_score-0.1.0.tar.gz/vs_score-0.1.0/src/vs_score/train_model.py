"""
train_model.py

Trains a logistic regression model to predict volleyball match outcomes using engineered features.
Outputs the trained model as 'logreg_model.pkl'.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Read the encoded feature data
df = pd.read_csv("csv/match_features_encoded.csv")

# Target variable: Does Team1 win? (MatchResult == 1)
df["target"] = (df["MatchResult"] == 1).astype(int)

feature_cols = [
    "Team1_encoded", "Team2_encoded",
    "Team1_last5_win_rate", "Team1_last5_avg_score", "Team1_last5_avg_concede",
    "Team2_last5_win_rate", "Team2_last5_avg_score", "Team2_last5_avg_concede",
    "h2h_team1_win_rate"
]

X = df[feature_cols]
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic Regression
lr = LogisticRegression(max_iter=1000)
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_lr))
print(classification_report(y_test, y_pred_lr))

# Save the model
with open("logreg_model.pkl", "wb") as f:
    pickle.dump(lr, f)
print("Logistic Regression model has been saved as 'logreg_model.pkl'.") 