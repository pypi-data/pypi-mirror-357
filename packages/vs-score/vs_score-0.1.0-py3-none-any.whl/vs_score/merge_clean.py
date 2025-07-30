"""
merge_clean.py

Cleans and merges multiple volleyball match CSV files with varying formats into a single, consistent dataset.
Removes duplicates, invalid rows, and adds match result labels. Output is saved to 'csv/clean_matches.csv'.
"""

import pandas as pd
import os
import glob
import re

def is_valid_date(val):
    """
    Check if a value is a valid date in the format YYYY-MM-DD.

    Args:
        val (str): Date string to check.

    Returns:
        bool: True if valid date, False otherwise.
    """
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}", str(val).strip()))

def get_match_result(row):
    """
    Calculate the match result label from a row's score.

    Args:
        row (pd.Series): Row containing 'Score' in 'X:Y' format.

    Returns:
        int or None: 1 if Team1 wins, 2 if Team2 wins, 0 if draw, None if invalid.
    """
    try:
        score1, score2 = map(int, row["Score"].split(":"))
        if score1 > score2:
            return 1
        elif score2 > score1:
            return 2
        else:
            return 0
    except:
        return None

csv_files = sorted(glob.glob("data/*.csv"))
all_cleaned = []

for file in csv_files:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        print(f"Could not read file ({file}): {e}")
        continue

    # 1. Format: info 2, team_name, guest, score
    if all(col in df.columns for col in ["info 2", "team_name", "guest", "score"]):
        cleaned = pd.DataFrame({
            "Date": df["info 2"],
            "Team1": df["team_name"],
            "Team2": df["guest"],
            "Score": df["score"]
        })
        cleaned = cleaned[cleaned["Team1"] != cleaned["Team2"]]
        all_cleaned.append(cleaned)
        continue

    # 2. Format: info 2, team_name, score (stacked team names)
    if all(col in df.columns for col in ["info 2", "team_name", "score"]):
        team_names = df["team_name"].reset_index(drop=True)
        half = len(team_names) // 2
        if len(team_names) % 2 != 0 or half == 0:
            print(f"Number of teams is not even, file skipped: {file}")
            continue

        team1 = team_names[:half]
        team2 = team_names[half:half * 2]

        cleaned = pd.DataFrame({
            "Date": df["info 2"][:half].values,
            "Team1": team1.values,
            "Team2": team2.values,
            "Score": df["score"][:half].values
        })
        cleaned = cleaned[cleaned["Team1"] != cleaned["Team2"]]
        all_cleaned.append(cleaned)
        continue

    # 3. Format: Date, Team1, Team2, Score (direct match format)
    if all(col in df.columns for col in ["Date", "Team1", "Team2", "Score"]):
        cleaned = df[["Date", "Team1", "Team2", "Score"]].copy()
        cleaned = cleaned[cleaned["Team1"] != cleaned["Team2"]]
        all_cleaned.append(cleaned)
        continue

if not all_cleaned:
    print("No files were processed!")
    exit()

final_df = pd.concat(all_cleaned, ignore_index=True)

# Remove duplicate rows
final_df = final_df.drop_duplicates(subset=["Date", "Team1", "Team2", "Score"])

# Remove rows without score or with 0:0 score
final_df = final_df[final_df["Score"].notna()]
final_df["Score_clean"] = final_df["Score"].astype(str).str.replace(" ", "")
final_df = final_df[final_df["Score_clean"] != ""]
final_df = final_df[final_df["Score_clean"] != "0:0"]

# Remove rows without date
final_df = final_df[final_df["Date"].notna()]
final_df["Date_clean"] = final_df["Date"].astype(str).str.strip()
final_df = final_df[final_df["Date_clean"] != ""]
final_df = final_df[~final_df["Date_clean"].str.startswith(",")]
final_df = final_df[final_df["Date_clean"].astype(str).str.lower() != "nat"]
final_df = final_df[~final_df["Date_clean"].astype(str).str.match(r"^\s*,")]
final_df = final_df[~final_df.apply(lambda row: str(row["Date"]).strip() == "" or str(row["Date"]).strip().startswith(","), axis=1)]

# Use cleaned columns
final_df["Score"] = final_df["Score_clean"]
final_df["Date"] = final_df["Date_clean"]
final_df = final_df.drop(columns=["Score_clean", "Date_clean"])

# Keep only rows with valid date
final_df = final_df[final_df["Date"].apply(is_valid_date)].copy()

# Add match result label
final_df["MatchResult"] = final_df.apply(get_match_result, axis=1)
final_df.dropna(subset=["MatchResult"], inplace=True)

# Sort by date
try:
    final_df["Date"] = pd.to_datetime(final_df["Date"], errors="coerce")
    final_df = final_df.sort_values("Date")
except:
    pass

final_df.to_csv("csv/clean_matches.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ {len(final_df)} matches cleaned and saved to 'csv/clean_matches.csv'.")