import pandas as pd
import os
import glob


csv_files = sorted(glob.glob("data/*.csv"))

all_cleaned = []

for file in csv_files:
    df = pd.read_csv(file)


    if "info 2" in df.columns and "team_name" in df.columns and "score" in df.columns:
        try:
            team_names = df.loc[:, "team_name"].reset_index(drop=True)
            half = len(team_names) // 2
            team1 = team_names[:half]
            team2 = team_names[half:half * 2]

            cleaned = pd.DataFrame({
                "Date": df["info 2"][:half].values,
                "Team1": team1.values,
                "Team2": team2.values,
                "Score": df["score"][:half].values
            })

            cleaned = cleaned[cleaned["Team1"] != cleaned["Team2"]]

            cleaned["SourceFile"] = os.path.basename(file)
            all_cleaned.append(cleaned)

        except Exception as e:
            print(f"Hata oluştu ({file}): {e}")


final_df = pd.concat(all_cleaned, ignore_index=True)

# Kazanan etiketini ekle (Label: Team1 kazandıysa 1, Team2 kazandıysa 2, berabere 0)
def get_match_result(row):
    try:
        score1, score2 = map(int, row["Score"].split(":"))
        if score1 > score2:
            return 1  # Team1 kazandı
        elif score2 > score1:
            return 2  # Team2 kazandı
        else:
            return 0  # Berabere
    except:
        return None

final_df["MatchResult"] = final_df.apply(get_match_result, axis=1)

#  Eksik skorları olan satırları at
final_df.dropna(subset=["MatchResult", "Score"], inplace=True)


final_df.to_csv("international_matches_clean.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ {len(final_df)} maç temizlendi ve 'international_matches_clean.csv' dosyasına kaydedildi.")
