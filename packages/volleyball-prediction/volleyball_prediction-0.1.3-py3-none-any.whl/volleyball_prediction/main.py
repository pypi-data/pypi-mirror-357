from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI(title="Voleybol Maç Tahmin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_data = joblib.load('volley_model.pkl')
model = model_data['model']
le_teams = model_data['label_encoder_teams']
feature_names = model_data['feature_names']

class MatchInput(BaseModel):
    team1: str
    team2: str
    team1_last_5_win_rate: float
    team2_last_5_win_rate: float
    last_match_result: int
    team1_historical_avg_score_diff: float
    team2_historical_avg_score_diff: float
    team1_last_5_sets_avg: float
    team2_last_5_sets_avg: float

class PredictionResponse(BaseModel):
    predicted_result: int
    result_explanation: str
    win_probability_team1: float
    win_probability_team2: float
    draw_probability: float

@app.post("/predict", response_model=PredictionResponse)
def predict_match(match_data: MatchInput):
    try:
        team1_encoded = le_teams.transform([match_data.team1])[0]
        team2_encoded = le_teams.transform([match_data.team2])[0]
        features = pd.DataFrame([[team1_encoded, team2_encoded,
                                  match_data.team1_last_5_win_rate, match_data.team2_last_5_win_rate,
                                  match_data.last_match_result,
                                  match_data.team1_historical_avg_score_diff, match_data.team2_historical_avg_score_diff,
                                  match_data.team1_last_5_sets_avg, match_data.team2_last_5_sets_avg]],
                                columns=feature_names)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        result_map = {
            0: "Berabere",
            1: f"{match_data.team1} kazanır",
            2: f"{match_data.team2} kazanır"
        }
        return PredictionResponse(
            predicted_result=int(prediction),
            result_explanation=result_map[prediction],
            win_probability_team1=float(probabilities[1]),
            win_probability_team2=float(probabilities[2]),
            draw_probability=float(probabilities[0])
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/teams")
def get_available_teams():
    all_teams = sorted(list(le_teams.classes_))
    return {"teams": all_teams}

@app.get("/team_stats")
def get_team_stats(team: str):
    df = pd.read_csv('international_matches_features.csv')
    matches = df[(df['Team1'] == team) | (df['Team2'] == team)].sort_values('Date')
    win_rate = matches['team1_last_5_win_rate'].iloc[-1] if not matches.empty else 0.5
    score_diff = matches['team1_historical_avg_score_diff'].iloc[-1] if not matches.empty else 0
    sets_avg = matches['team1_last_5_sets_avg'].iloc[-1] if not matches.empty else 0
    return {
        'win_rate': float(win_rate),
        'score_diff': float(score_diff),
        'goals_avg': float(sets_avg)
    }

@app.get("/last_match_result")
def get_last_match_result(team1: str, team2: str):
    df = pd.read_csv('international_matches_features.csv')
    matches = df[((df['Team1'] == team1) & (df['Team2'] == team2)) |
                 ((df['Team1'] == team2) & (df['Team2'] == team1))]
    matches = matches.sort_values('Date')
    if not matches.empty:
        last_result = int(matches.iloc[-1]['MatchResult'])
        # Eğer sıralar tersse sonucu tersle
        if matches.iloc[-1]['Team1'] == team2 and matches.iloc[-1]['Team2'] == team1:
            if last_result == 1:
                last_result = 2
            elif last_result == 2:
                last_result = 1
    else:
        last_result = 0
    return {"last_match_result": last_result}