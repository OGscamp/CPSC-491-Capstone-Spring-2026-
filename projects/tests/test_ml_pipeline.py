import json
import os
import sys
import tempfile

import pandas as pd
import pytest


THIS_DIR = os.path.dirname(__file__)
ML_SCRIPTS_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "ML Scripts"))
sys.path.append(ML_SCRIPTS_DIR)

from feature_engineering import extract_team_features
from dataset_builder import build_dataset


def _make_match_json(team1_win=True):
    def make_player(kills, assists, gold, cs, jungle, vision):
        return {
            "kills": kills,
            "assists": assists,
            "goldEarned": gold,
            "totalMinionsKilled": cs,
            "neutralMinionsKilled": jungle,
            "visionScore": vision,
        }

    team1 = [
        make_player(2, 3, 5000, 50, 10, 8),
        make_player(1, 4, 4800, 45, 8, 7),
        make_player(0, 5, 4700, 60, 6, 9),
        make_player(3, 2, 5100, 55, 12, 6),
        make_player(2, 1, 4900, 52, 9, 5),
    ]
    team2 = [
        make_player(1, 2, 4500, 40, 7, 6),
        make_player(0, 3, 4300, 35, 5, 7),
        make_player(2, 1, 4600, 48, 8, 5),
        make_player(1, 2, 4400, 42, 6, 4),
        make_player(0, 1, 4200, 38, 4, 6),
    ]

    match_json = {
        "info": {
            "participants": team1 + team2,
            "teams": [
                {
                    "teamId": 100,
                    "win": team1_win,
                    "objectives": {
                        "tower": {"kills": 5},
                        "dragon": {"kills": 2},
                        "baron": {"kills": 1},
                    },
                },
                {
                    "teamId": 200,
                    "win": not team1_win,
                    "objectives": {
                        "tower": {"kills": 3},
                        "dragon": {"kills": 1},
                        "baron": {"kills": 0},
                    },
                },
            ],
        }
    }
    return match_json


def test_extract_team_features_returns_expected_keys():
    match_json = _make_match_json(team1_win=True)
    features = extract_team_features(match_json)
    expected_keys = {
        "gold_diff",
        "kill_diff",
        "assist_diff",
        "cs_diff",
        "vision_diff",
        "tower_diff",
        "dragon_diff",
        "baron_diff",
        "win",
    }
    assert expected_keys.issubset(set(features.keys()))
    assert features["win"] == 1


def test_build_dataset_from_json_files():
    match1 = _make_match_json(team1_win=True)
    match2 = _make_match_json(team1_win=False)

    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "match1.json")
        file2 = os.path.join(tmpdir, "match2.json")
        with open(file1, "w", encoding="utf-8") as f:
            json.dump(match1, f)
        with open(file2, "w", encoding="utf-8") as f:
            json.dump(match2, f)

        df = build_dataset([file1, file2])

    assert df.shape[0] == 2
    assert "win" in df.columns
    assert df["win"].tolist() == [1, 0]


def test_xgboost_training_creates_model_file():
    pytest.importorskip("xgboost")
    from xgboost_model import train_xgboost

    df = pd.DataFrame(
        [
            {"gold_diff": 1000, "kill_diff": 5, "assist_diff": 8, "cs_diff": 30, "vision_diff": 10, "tower_diff": 2, "dragon_diff": 1, "baron_diff": 0, "win": 1},
            {"gold_diff": -500, "kill_diff": -3, "assist_diff": -4, "cs_diff": -15, "vision_diff": -6, "tower_diff": -1, "dragon_diff": 0, "baron_diff": 0, "win": 0},
            {"gold_diff": 800, "kill_diff": 2, "assist_diff": 6, "cs_diff": 20, "vision_diff": 7, "tower_diff": 1, "dragon_diff": 1, "baron_diff": 0, "win": 1},
            {"gold_diff": -700, "kill_diff": -2, "assist_diff": -5, "cs_diff": -18, "vision_diff": -8, "tower_diff": -2, "dragon_diff": -1, "baron_diff": 0, "win": 0},
            {"gold_diff": 1200, "kill_diff": 6, "assist_diff": 10, "cs_diff": 35, "vision_diff": 12, "tower_diff": 3, "dragon_diff": 2, "baron_diff": 1, "win": 1},
            {"gold_diff": -900, "kill_diff": -4, "assist_diff": -6, "cs_diff": -25, "vision_diff": -9, "tower_diff": -2, "dragon_diff": -1, "baron_diff": 0, "win": 0},
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "tiny_dataset.csv")
        model_path = os.path.join(tmpdir, "xgb_model.json")
        df.to_csv(csv_path, index=False)

        results = train_xgboost(csv_path, model_path, test_size=0.33, seed=7)

        assert os.path.exists(model_path)
        assert results["rows"] == df.shape[0]
