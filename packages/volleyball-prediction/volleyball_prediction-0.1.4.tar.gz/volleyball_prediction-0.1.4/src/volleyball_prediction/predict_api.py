from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn
import os

print("--- PREDICT_API.PY DOSYASI BAŞARIYLA YÜKLENDİ ---")

app = FastAPI(title="Voleybol Maç Tahmin API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML sunmak için kök endpoint
@app.get("/", response_class=HTMLResponse)
def serve_html():
    with open(os.path.join(os.path.dirname(__file__), "frontend", "index_fixed.html"), "r", encoding="utf-8") as f:
        return f.read()

# Model ve dönüştürücüler
try:
    model_data = joblib.load('volley_model.pkl')
    model = model_data['model']
    le_teams = model_data['label_encoder_teams']
    feature_names = model_data['feature_names']
except FileNotFoundError:
    raise RuntimeError("volley_model.pkl bulunamadı. Önce train_model.py çalıştırılmalı.")

# Veri giriş modeli
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

# Yanıt modeli
class PredictionResponse(BaseModel):
    predicted_result: int
    result_explanation: str
    win_probability_team1: float
    win_probability_team2: float
    draw_probability: float

# Tahmin endpoint'i
@app.post("/predict", response_model=PredictionResponse)
def predict_match(match_input: MatchInput):
    data = match_input.dict()
    team1_original = data['team1']
    team2_original = data['team2']
    swapped = False

    if team1_original > team2_original:
        swapped = True
        team1, team2 = team2_original, team1_original
        data['team1_last_5_win_rate'], data['team2_last_5_win_rate'] = data['team2_last_5_win_rate'], data['team1_last_5_win_rate']
        data['team1_historical_avg_score_diff'], data['team2_historical_avg_score_diff'] = data['team2_historical_avg_score_diff'], data['team1_historical_avg_score_diff']
        data['team1_last_5_sets_avg'], data['team2_last_5_sets_avg'] = data['team2_last_5_sets_avg'], data['team1_last_5_sets_avg']
        if data['last_match_result'] == 1:
            data['last_match_result'] = 2
        elif data['last_match_result'] == 2:
            data['last_match_result'] = 1
    else:
        team1, team2 = team1_original, team2_original

    input_df = pd.DataFrame([data])
    try:
        input_df['Team1_encoded'] = le_teams.transform([team1])
        input_df['Team2_encoded'] = le_teams.transform([team2])
    except ValueError as e:
        unseen = [t for t in [team1, team2] if t not in le_teams.classes_]
        raise HTTPException(status_code=400, detail=f"Model bu takımları tanımıyor: {unseen}. Hata: {e}")

    try:
        X_pred = input_df[feature_names]
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Model için beklenen bir özellik eksik: {e}")

    prediction = model.predict(X_pred)
    probabilities = model.predict_proba(X_pred)[0]
    predicted_result = int(prediction[0])

    if swapped:
        if predicted_result == 1:
            predicted_result = 2
        elif predicted_result == 2:
            predicted_result = 1

    result_map = {1: f"{team1_original} kazanır", 2: f"{team2_original} kazanır", 0: "Beraberlik"}
    explanation = result_map.get(predicted_result, "Bilinmeyen sonuç")

    class_order = list(model.classes_)
    prob_draw = probabilities[class_order.index(0)]
    prob_win1_sorted = probabilities[class_order.index(1)]
    prob_win2_sorted = probabilities[class_order.index(2)]

    if swapped:
        win_probability_team1 = prob_win2_sorted
        win_probability_team2 = prob_win1_sorted
    else:
        win_probability_team1 = prob_win1_sorted
        win_probability_team2 = prob_win2_sorted

    return PredictionResponse(
        predicted_result=predicted_result,
        result_explanation=explanation,
        win_probability_team1=win_probability_team1,
        win_probability_team2=win_probability_team2,
        draw_probability=prob_draw
    )

# Yardımcı endpoint'ler
@app.get("/teams")
def get_available_teams():
    return {"teams": sorted(list(le_teams.classes_))}

@app.get("/team_stats")
def get_team_stats(team: str):
    try:
        df = pd.read_csv('international_matches_features.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Dosya bulunamadı: international_matches_features.csv")
    
    matches = df[(df['Team1'] == team) | (df['Team2'] == team)].sort_values('Date')
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Takım için istatistik yok: {team}")

    last = matches.iloc[-1]
    if last['Team1'] == team:
        return {
            'win_rate': float(last['team1_last_5_win_rate']),
            'score_diff': float(last['team1_historical_avg_score_diff']),
            'sets_avg': float(last['team1_last_5_sets_avg'])
        }
    else:
        return {
            'win_rate': float(last['team2_last_5_win_rate']),
            'score_diff': float(last['team2_historical_avg_score_diff']),
            'sets_avg': float(last['team2_last_5_sets_avg'])
        }

@app.get("/last_match_result")
def get_last_match_result(team1: str, team2: str):
    try:
        df = pd.read_csv('international_matches_features.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Dosya bulunamadı: international_matches_features.csv")

    matches = df[((df['Team1'] == team1) & (df['Team2'] == team2)) | ((df['Team1'] == team2) & (df['Team2'] == team1))].sort_values('Date')
    if not matches.empty:
        last = matches.iloc[-1]
        result = int(last['MatchResult'])
        if last['Team1'] == team2 and last['Team2'] == team1:
            if result == 1:
                result = 2
            elif result == 2:
                result = 1
        return {"last_match_result": result}
    return {"last_match_result": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
