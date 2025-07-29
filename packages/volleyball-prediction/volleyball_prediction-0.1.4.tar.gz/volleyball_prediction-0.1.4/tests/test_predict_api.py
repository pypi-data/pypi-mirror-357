from fastapi.testclient import TestClient
from src.volleyball_prediction.predict_api import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 404  # çünkü root yok, varsa 200 yaparsın

def test_predict_endpoint_exists():
    response = client.post("/predict", json={
        "team1": "Türkiye",
        "team2": "Sırbistan",
        "team1_last_5_win_rate": 0.8,
        "team2_last_5_win_rate": 0.6,
        "last_match_result": 1,
        "team1_historical_avg_score_diff": 2.1,
        "team2_historical_avg_score_diff": -1.4,
        "team1_last_5_sets_avg": 3.2,
        "team2_last_5_sets_avg": 2.8
    })
    assert response.status_code == 200
    assert "predicted_result" in response.json()
    assert "result_explanation" in response.json()
