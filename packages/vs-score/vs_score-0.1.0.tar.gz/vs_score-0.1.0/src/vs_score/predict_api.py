"""
predict_api.py

FastAPI backend for volleyball match outcome prediction. Serves a REST API for team listing and match prediction, and serves the frontend web interface.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import pickle
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Initialize FastAPI app
app = FastAPI(title="Volleyball Match Prediction API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model and features
with open('logreg_model.pkl', 'rb') as f:
    model = pickle.load(f)
features_df = pd.read_csv('csv/match_features_encoded.csv')

# Recreate label encoder for team names
from sklearn.preprocessing import LabelEncoder
le_teams = LabelEncoder()
all_teams = pd.concat([features_df["Team1"], features_df["Team2"]]).unique()
le_teams.fit(all_teams)

# Request/response schemas
class MatchInput(BaseModel):
    team1: str
    team2: str

class PredictionResponse(BaseModel):
    team1: str
    team2: str
    win_probability_team1: float
    win_probability_team2: float

@app.post("/predict", response_model=PredictionResponse)
def predict_match(match_data: MatchInput):
    """
    Predict the win probabilities for a given volleyball match.

    :param match_data: Input data containing team1 and team2 names.
    :type match_data: MatchInput
    :return: Predicted win probabilities for both teams.
    :rtype: PredictionResponse
    :raises HTTPException: If not enough data for the selected teams or other errors occur.
    """
    try:
        # Encode team names
        team1_encoded = le_teams.transform([match_data.team1])[0]
        team2_encoded = le_teams.transform([match_data.team2])[0]

        # Find the most recent feature row for the matchup
        row = features_df[(features_df["Team1"] == match_data.team1) & (features_df["Team2"] == match_data.team2)].tail(1)
        if row.empty:
            row1 = features_df[features_df["Team1"] == match_data.team1].tail(1)
            row2 = features_df[features_df["Team2"] == match_data.team2].tail(1)
            if row1.empty or row2.empty:
                raise HTTPException(status_code=400, detail="Not enough data for the selected teams.")
            row = row1.copy()
            for col in ["Team2_encoded", "Team2_last5_win_rate", "Team2_last5_avg_score", "Team2_last5_avg_concede"]:
                row[col] = row2.iloc[0][col]

        feature_cols = [
            "Team1_encoded", "Team2_encoded",
            "Team1_last5_win_rate", "Team1_last5_avg_score", "Team1_last5_avg_concede",
            "Team2_last5_win_rate", "Team2_last5_avg_score", "Team2_last5_avg_concede",
            "h2h_team1_win_rate"
        ]
        X = row[feature_cols]
        proba = model.predict_proba(X)[0]
        return PredictionResponse(
            team1=match_data.team1,
            team2=match_data.team2,
            win_probability_team1=round(proba[1]*100, 2),
            win_probability_team2=round(proba[0]*100, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/teams")
def get_available_teams():
    """
    Return the list of all available teams in the system.

    :return: Dictionary with a list of team names.
    :rtype: dict
    """
    all_teams_sorted = sorted(list(le_teams.classes_))
    return {"teams": all_teams_sorted}

# Serve static files (frontend directory)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/", include_in_schema=False)
def root():
    """
    Serve the frontend index.html file.

    :return: FileResponse for the index.html file.
    :rtype: FileResponse
    """
    return FileResponse(os.path.join("frontend", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("predict_api:app", host="0.0.0.0", port=8000, reload=True)