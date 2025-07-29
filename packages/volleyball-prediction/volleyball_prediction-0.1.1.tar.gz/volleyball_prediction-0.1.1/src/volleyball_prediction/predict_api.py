from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn

# predict_api.py dosyasının başı

from fastapi import FastAPI, HTTPException
# ... diğer importlar ...
import uvicorn

print("--- PREDICT_API.PY DOSYASI BAŞARIYLA YÜKLENDİ ---") # <--- BU SATIRI EKLEYİN

# API uygulamasını başlat
app = FastAPI(title="Voleybol Maç Tahmin API")

# ... kodun geri kalanı ...
# API uygulamasını başlat
app = FastAPI(title="Voleybol Maç Tahmin API")

# CORS ayarlarını ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver (geliştirme için)
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodlarına izin ver
    allow_headers=["*"],  # Tüm headerlara izin ver
)

# Model ve gerekli dönüştürücüleri yükle
try:
    model_data = joblib.load('volley_model.pkl')
    model = model_data['model']
    le_teams = model_data['label_encoder_teams']
    feature_names = model_data['feature_names']
except FileNotFoundError:
    raise RuntimeError("volley_model.pkl dosyası bulunamadı. Lütfen önce train_model.py betiğini çalıştırın.")

# Kullanıcıdan beklenen veri şeması
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

# API'nin döndüreceği yanıt şeması
class PredictionResponse(BaseModel):
    predicted_result: int
    result_explanation: str
    win_probability_team1: float
    win_probability_team2: float
    draw_probability: float

# --- DÜZELTİLMİŞ TAHMİN FONKSİYONU ---
@app.post("/predict", response_model=PredictionResponse)
def predict_match(match_input: MatchInput):
    """
    Verilen maç bilgileriyle maç sonucunu tahmin eder.
    Takım sırasından bağımsız, tutarlı sonuçlar üretmek için
    takımları ve özellikleri alfabetik olarak sıralar.
    """
    
    # Girdileri bir sözlüğe çevir
    data = match_input.dict()
    team1_original = data['team1']
    team2_original = data['team2']
    
    # 1. Takımları alfabetik olarak sırala ve özellikleri de bu sıraya göre ayarla
    swapped = False
    if team1_original > team2_original:
        swapped = True
        # Takım isimlerini ve ilgili istatistikleri değiştir
        team1, team2 = team2_original, team1_original
        
        data['team1_last_5_win_rate'], data['team2_last_5_win_rate'] = \
            data['team2_last_5_win_rate'], data['team1_last_5_win_rate']
            
        data['team1_historical_avg_score_diff'], data['team2_historical_avg_score_diff'] = \
            data['team2_historical_avg_score_diff'], data['team1_historical_avg_score_diff']
            
        data['team1_last_5_sets_avg'], data['team2_last_5_sets_avg'] = \
            data['team2_last_5_sets_avg'], data['team1_last_5_sets_avg']
        
        # Son maç sonucunu da tersine çevir (1 ise 2, 2 ise 1 yap)
        if data['last_match_result'] == 1:
            data['last_match_result'] = 2
        elif data['last_match_result'] == 2:
            data['last_match_result'] = 1
    else:
        team1, team2 = team1_original, team2_original

    # 2. Model için DataFrame'i hazırla
    input_df = pd.DataFrame([data])
    
    # Takım isimlerini LabelEncoder ile dönüştür
    try:
        # Sıralanmış takım isimlerini kullan
        input_df['Team1_encoded'] = le_teams.transform([team1])
        input_df['Team2_encoded'] = le_teams.transform([team2])
    except ValueError as e:
        unseen_teams = [t for t in [team1, team2] if t not in le_teams.classes_]
        raise HTTPException(status_code=400, detail=f"Model bu takımları tanımıyor: {unseen_teams}. Hata: {e}")

    # Modelin beklediği sırayla özellikleri seç
    try:
        X_pred = input_df[feature_names]
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Model için beklenen bir özellik eksik: {e}")

    # 3. Tahmini yap
    prediction = model.predict(X_pred)
    probabilities = model.predict_proba(X_pred)[0]
    
    predicted_result = int(prediction[0])
    
    # 4. Eğer takımları başta çevirdiysek, sonucu orijinal sıraya göre geri çevir
    if swapped:
        if predicted_result == 1:
            predicted_result = 2
        elif predicted_result == 2:
            predicted_result = 1
            
    # Sonuç açıklamasını oluştur (her zaman orijinal takım isimlerini kullan)
    result_map = {1: f"{team1_original} kazanır", 2: f"{team2_original} kazanır", 0: "Beraberlik"}
    explanation = result_map.get(predicted_result, "Bilinmeyen sonuç")

    # Olasılıkları doğru takımlara ata
    # Modelin class sıralamasını kontrol et (genellikle [0, 1, 2] olur)
    class_order = list(model.classes_)
    prob_draw = probabilities[class_order.index(0)]
    prob_win1_sorted = probabilities[class_order.index(1)] # Alfabetik ilk takımın kazanma olasılığı
    prob_win2_sorted = probabilities[class_order.index(2)] # Alfabetik ikinci takımın kazanma olasılığı

    if swapped:
         # Eğer takas yapıldıysa, olasılıkları da takasla
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

# --- YARDIMCI ENDPOINT'LER (DEĞİŞİKLİK YOK) ---

@app.get("/teams")
def get_available_teams():
    """
    Modelin tanıdığı tüm takımların listesini döndürür.
    """
    all_teams = sorted(list(le_teams.classes_))
    return {"teams": all_teams}

@app.get("/team_stats")
def get_team_stats(team: str):
    """
    Belirtilen takım için en son hesaplanmış istatistikleri döndürür.
    Bu endpoint frontend'in otomatik veri doldurmasına yardımcı olur.
    """
    try:
        df = pd.read_csv('international_matches_features.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Özellik dosyası 'international_matches_features.csv' bulunamadı.")
    
    matches = df[(df['Team1'] == team) | (df['Team2'] == team)].sort_values('Date')
    
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Takım için istatistik bulunamadı: {team}")

    last_match = matches.iloc[-1]
    
    # Takımın Team1 mi Team2 mi olduğuna göre doğru istatistikleri al
    if last_match['Team1'] == team:
        win_rate = last_match['team1_last_5_win_rate']
        score_diff = last_match['team1_historical_avg_score_diff']
        sets_avg = last_match['team1_last_5_sets_avg']
    else:
        win_rate = last_match['team2_last_5_win_rate']
        score_diff = last_match['team2_historical_avg_score_diff']
        sets_avg = last_match['team2_last_5_sets_avg']

    return {
        'win_rate': float(win_rate),
        'score_diff': float(score_diff),
        'sets_avg': float(sets_avg)
    }

@app.get("/last_match_result")
def get_last_match_result(team1: str, team2: str):
    """
    İki takımın en son karşılaştığı maçtaki sonucu döndürür.
    Sonuç her zaman çağrıyı yapan team1'in perspektifinden verilir.
    (1: team1 kazandı, 2: team2 kazandı, 0: Sonuç yok/berabere)
    """
    try:
        df = pd.read_csv('international_matches_features.csv')
    except FileNotFoundError:
         raise HTTPException(status_code=500, detail="Özellik dosyası 'international_matches_features.csv' bulunamadı.")

    matches = df[((df['Team1'] == team1) & (df['Team2'] == team2)) |
                 ((df['Team1'] == team2) & (df['Team2'] == team1))]
    matches = matches.sort_values('Date')
    
    if not matches.empty:
        last_match_row = matches.iloc[-1]
        last_result = int(last_match_row['MatchResult'])
        
        # Eğer sorgudaki team1, datadaki team2 ise, sonucu ters çevir
        if last_match_row['Team1'] == team2 and last_match_row['Team2'] == team1:
             if last_result == 1:
                 last_result = 2
             elif last_result == 2:
                 last_result = 1
        return {"last_match_result": last_result}
    
    return {"last_match_result": 0} # Geçmiş maç yoksa 0 döndür


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)