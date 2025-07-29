import pandas as pd
import numpy as np

input_path = "international_matches_clean.csv"
output_path = "international_matches_features.csv"

df = pd.read_csv(input_path)
df['Date'] = pd.to_datetime(df['Date'], format='mixed')
df = df.sort_values('Date').reset_index(drop=True)

features = []

for idx, row in df.iterrows():
    t1 = row['Team1']
    t2 = row['Team2']
    date = row['Date']

    # Team1 geçmiş maçlar
    t1_matches = df[((df['Team1'] == t1) | (df['Team2'] == t1)) & (df['Date'] < date)]
    t1_last5 = t1_matches.tail(5)
    t1_win = ((t1_last5['Team1'] == t1) & (t1_last5['MatchResult'] == 1)) | ((t1_last5['Team2'] == t1) & (t1_last5['MatchResult'] == 2))
    t1_win_rate = t1_win.mean() if len(t1_last5) > 0 else 0.5
    t1_score_diff = []
    t1_sets = []
    for _, r in t1_last5.iterrows():
        s1, s2 = map(int, r['Score'].split(':'))
        if r['Team1'] == t1:
            t1_score_diff.append(s1 - s2)
            t1_sets.append(s1)
        else:
            t1_score_diff.append(s2 - s1)
            t1_sets.append(s2)
    t1_score_diff_avg = np.mean(t1_score_diff) if t1_score_diff else 0
    t1_sets_avg = np.mean(t1_sets) if t1_sets else 0

    # Team2 geçmiş maçlar
    t2_matches = df[((df['Team1'] == t2) | (df['Team2'] == t2)) & (df['Date'] < date)]
    t2_last5 = t2_matches.tail(5)
    t2_win = ((t2_last5['Team1'] == t2) & (t2_last5['MatchResult'] == 1)) | ((t2_last5['Team2'] == t2) & (t2_last5['MatchResult'] == 2))
    t2_win_rate = t2_win.mean() if len(t2_last5) > 0 else 0.5
    t2_score_diff = []
    t2_sets = []
    for _, r in t2_last5.iterrows():
        s1, s2 = map(int, r['Score'].split(':'))
        if r['Team1'] == t2:
            t2_score_diff.append(s1 - s2)
            t2_sets.append(s1)
        else:
            t2_score_diff.append(s2 - s1)
            t2_sets.append(s2)
    t2_score_diff_avg = np.mean(t2_score_diff) if t2_score_diff else 0
    t2_sets_avg = np.mean(t2_sets) if t2_sets else 0

    # Son karşılaşma sonucu (simetrik olacak şekilde)
    last_match = df[((df['Team1'] == t1) & (df['Team2'] == t2)) | ((df['Team1'] == t2) & (df['Team2'] == t1)) & (df['Date'] < date)]
    if not last_match.empty:
        last_result = int(last_match.iloc[-1]['MatchResult'])
        # Eğer son maçta t1 Team2 ise, sonucu tersle
        if last_match.iloc[-1]['Team1'] == t2 and last_match.iloc[-1]['Team2'] == t1:
            if last_result == 1:
                last_result = 2
            elif last_result == 2:
                last_result = 1
    else:
        last_result = 0

    features.append({
        'Date': date,
        'Team1': t1,
        'Team2': t2,
        'Score': row['Score'],
        'MatchResult': row['MatchResult'],
        'team1_last_5_win_rate': t1_win_rate,
        'team2_last_5_win_rate': t2_win_rate,
        'last_match_result': last_result,
        'team1_historical_avg_score_diff': t1_score_diff_avg,
        'team2_historical_avg_score_diff': t2_score_diff_avg,
        'team1_last_5_sets_avg': t1_sets_avg,
        'team2_last_5_sets_avg': t2_sets_avg
    })

features_df = pd.DataFrame(features)
features_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f'✅ Özellik çıkarımı tamamlandı. Kaydedilen dosya: {output_path}')