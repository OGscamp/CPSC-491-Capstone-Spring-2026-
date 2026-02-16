import json
import pandas as pd
from feature_engineering import extract_team_features


def build_dataset(match_files):
    rows = []

    for file in match_files:
        with open(file, "r") as f:
            match_json = json.load(f)

        features = extract_team_features(match_json)
        rows.append(features)

    df = pd.DataFrame(rows)
    df.fillna(0, inplace=True)

    return df


if __name__ == "__main__":
    import glob

    files = glob.glob("matches/*.json")
    dataset = build_dataset(files)

    dataset.to_csv("matches_dataset.csv", index=False)
    print("Dataset created:", dataset.shape)