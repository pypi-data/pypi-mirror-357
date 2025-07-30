"""
feature_engineering.py

Performs feature engineering and encoding for volleyball match data. Generates rolling statistics, head-to-head win rates, encodes team names, and fills missing values. Outputs the final feature set for model training.
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder

# 1. Read cleaned matches
matches = pd.read_csv("csv/clean_matches.csv")
matches["Date"] = pd.to_datetime(matches["Date"])
matches = matches.sort_values("Date")

# 2. Split score into two columns
score_split = matches["Score"].str.split(":", expand=True)
matches["Score1"] = score_split[0].astype(int)
matches["Score2"] = score_split[1].astype(int)

# 3. Add MatchResult if not present
if "MatchResult" not in matches.columns:
    def get_match_result(row):
        """
        Calculate the match result label from a row's score.

        :param row: Row containing 'Score1' and 'Score2'.
        :type row: pd.Series
        :return: 1 if Team1 wins, 2 if Team2 wins, 0 if draw.
        :rtype: int
        """
        if row["Score1"] > row["Score2"]:
            return 1
        elif row["Score2"] > row["Score1"]:
            return 2
        else:
            return 0
    matches["MatchResult"] = matches.apply(get_match_result, axis=1)

N = 5  # Last N matches

def rolling_features(team_col, score_col, opp_score_col, result_col, N=5):
    """
    Calculate rolling win rate, average score, and average conceded score for a team.

    :param team_col: Column name for team.
    :type team_col: str
    :param score_col: Column name for team's score.
    :type score_col: str
    :param opp_score_col: Column name for opponent's score.
    :type opp_score_col: str
    :param result_col: Column name for win indicator.
    :type result_col: str
    :param N: Number of previous matches to consider.
    :type N: int
    :return: Tuple of lists (win_rate, avg_score, avg_concede).
    :rtype: tuple
    """
    features = []
    for idx, row in matches.iterrows():
        team = row[team_col]
        date = row["Date"]
        past_matches = matches[(matches[team_col] == team) & (matches["Date"] < date)].tail(N)
        if len(past_matches) == 0:
            features.append((None, None, None))
            continue
        win_rate = (past_matches[result_col] == 1).sum() / len(past_matches)
        avg_score = past_matches[score_col].mean()
        avg_concede = past_matches[opp_score_col].mean()
        features.append((win_rate, avg_score, avg_concede))
    return zip(*features)

# Team1 features
team1_win, team1_avg_score, team1_avg_concede = rolling_features(
    "Team1", "Score1", "Score2", "MatchResult", N
)
matches["Team1_last5_win_rate"] = list(team1_win)
matches["Team1_last5_avg_score"] = list(team1_avg_score)
matches["Team1_last5_avg_concede"] = list(team1_avg_concede)

# Team2 features (for Team2, win means MatchResult==2)
def team2_result(row):
    """
    Returns 1 if Team2 wins, 0 otherwise.

    :param row: Row containing 'MatchResult'.
    :type row: pd.Series
    :return: 1 if Team2 wins, 0 otherwise.
    :rtype: int
    """
    return 1 if row["MatchResult"] == 2 else 0
matches["MatchResult2"] = matches.apply(team2_result, axis=1)
team2_win, team2_avg_score, team2_avg_concede = rolling_features(
    "Team2", "Score2", "Score1", "MatchResult2", N
)
matches["Team2_last5_win_rate"] = list(team2_win)
matches["Team2_last5_avg_score"] = list(team2_avg_score)
matches["Team2_last5_avg_concede"] = list(team2_avg_concede)

def h2h_win_rate(row):
    """
    Calculate head-to-head win rate for Team1 against Team2.

    :param row: Row containing 'Team1', 'Team2', and 'Date'.
    :type row: pd.Series
    :return: Win rate of Team1 against Team2.
    :rtype: float or None
    """
    team1 = row["Team1"]
    team2 = row["Team2"]
    date = row["Date"]
    past = matches[
        ((matches["Team1"] == team1) & (matches["Team2"] == team2)) |
        ((matches["Team1"] == team2) & (matches["Team2"] == team1))
    ]
    past = past[past["Date"] < date]
    if len(past) == 0:
        return None
    team1_wins = ((past["Team1"] == team1) & (past["MatchResult"] == 1)).sum() + \
                 ((past["Team2"] == team1) & (past["MatchResult"] == 2)).sum()
    return team1_wins / len(past)
matches["h2h_team1_win_rate"] = matches.apply(h2h_win_rate, axis=1)

# Save intermediate features (optional)
matches.to_csv("csv/match_features.csv", index=False, encoding="utf-8-sig")
print("Feature engineering completed, features saved to 'csv/match_features.csv'.")

# 4. Encode team names
all_teams = pd.concat([matches["Team1"], matches["Team2"]]).unique()
le = LabelEncoder()
le.fit(all_teams)
matches["Team1_encoded"] = le.transform(matches["Team1"])
matches["Team2_encoded"] = le.transform(matches["Team2"])

# 5. Fill missing feature values with 0
feature_cols = [
    "Team1_last5_win_rate", "Team1_last5_avg_score", "Team1_last5_avg_concede",
    "Team2_last5_win_rate", "Team2_last5_avg_score", "Team2_last5_avg_concede",
    "h2h_team1_win_rate"
]
matches[feature_cols] = matches[feature_cols].fillna(0)

# 6. Save final encoded features
matches.to_csv("csv/match_features_encoded.csv", index=False, encoding="utf-8-sig")
print("Team names encoded and missing features filled. Final features saved to 'csv/match_features_encoded.csv'.") 