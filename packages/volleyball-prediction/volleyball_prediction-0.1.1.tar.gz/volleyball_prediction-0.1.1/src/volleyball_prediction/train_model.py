import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn.metrics import classification_report

df = pd.read_csv('international_matches_features.csv')

# Tek bir LabelEncoder ile tüm takımlar encode edilecek
all_teams = pd.concat([df['Team1'], df['Team2']]).unique()
le_teams = LabelEncoder()
le_teams.fit(all_teams)
df['Team1_encoded'] = le_teams.transform(df['Team1'])
df['Team2_encoded'] = le_teams.transform(df['Team2'])

# Simetrik veri oluştur
swapped = df.copy()
swapped['Team1'], swapped['Team2'] = df['Team2'], df['Team1']
swapped['Team1_encoded'], swapped['Team2_encoded'] = df['Team2_encoded'], df['Team1_encoded']
swapped['team1_last_5_win_rate'], swapped['team2_last_5_win_rate'] = df['team2_last_5_win_rate'], df['team1_last_5_win_rate']
swapped['team1_historical_avg_score_diff'], swapped['team2_historical_avg_score_diff'] = df['team2_historical_avg_score_diff'], df['team1_historical_avg_score_diff']
swapped['team1_last_5_sets_avg'], swapped['team2_last_5_sets_avg'] = df['team2_last_5_sets_avg'], df['team1_last_5_sets_avg']

# Sonuçları tersle

def swap_result(x):
    if x == 1:
        return 2
    elif x == 2:
        return 1
    else:
        return 0
swapped['MatchResult'] = df['MatchResult'].apply(swap_result)
swapped['last_match_result'] = df['last_match_result'].apply(swap_result)

full = pd.concat([df, swapped], ignore_index=True)

features = [
    'Team1_encoded', 'Team2_encoded',
    'team1_last_5_win_rate', 'team2_last_5_win_rate',
    'last_match_result',
    'team1_historical_avg_score_diff', 'team2_historical_avg_score_diff',
    'team1_last_5_sets_avg', 'team2_last_5_sets_avg'
]

X = full[features]
y = full['MatchResult']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"Eğitim seti doğruluk oranı: {model.score(X_train, y_train):.4f}")
print(f"Test seti doğruluk oranı: {model.score(X_test, y_test):.4f}")
print(classification_report(y_test, model.predict(X_test), digits=4))

model_data = {
    'model': model,
    'label_encoder_teams': le_teams,
    'feature_names': features
}
joblib.dump(model_data, 'volley_model.pkl')
print('✅ Model başarıyla eğitildi ve kaydedildi: volley_model.pkl')