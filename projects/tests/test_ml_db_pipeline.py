import importlib.util
import json
import os
import tempfile

import pandas as pd
import pytest


THIS_DIR = os.path.dirname(__file__)
ML_SCRIPTS_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "ML Scripts"))
DB_SCRIPT_PATH = os.path.join(ML_SCRIPTS_DIR, "build_dataset_from_db.py")
XGB_SCRIPT_PATH = os.path.join(ML_SCRIPTS_DIR, "xgboost_model.py")


def _load_module(module_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_match_json(match_id, team1_win=True):
    def make_player(kills, assists, gold, cs, jungle, vision):
        return {
            "kills": kills,
            "assists": assists,
            "goldEarned": gold,
            "totalMinionsKilled": cs,
            "neutralMinionsKilled": jungle,
            "visionScore": vision,
        }

    team1 = [make_player(4, 6, 12000, 150, 20, 25)] * 5
    team2 = [make_player(2, 3, 10000, 120, 15, 18)] * 5

    return {
        "metadata": {"matchId": match_id},
        "info": {
            "gameCreation": 1700000000000,
            "gameDuration": 1800,
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
                        "tower": {"kills": 2},
                        "dragon": {"kills": 1},
                        "baron": {"kills": 0},
                    },
                },
            ],
        },
    }


def test_build_dataset_from_db_writes_csv(monkeypatch):
    module = _load_module(DB_SCRIPT_PATH, "build_dataset_from_db_module")

    fake_recent = [{"match_id": "M1"}, {"match_id": "M2"}]
    fake_rows = {
        "M1": json.dumps(_make_match_json("M1", team1_win=True)),
        "M2": json.dumps(_make_match_json("M2", team1_win=False)),
    }

    monkeypatch.setattr(module, "get_recent_matches", lambda limit: fake_recent)
    monkeypatch.setattr(module, "get_raw_match_json", lambda match_id: fake_rows.get(match_id))

    with tempfile.TemporaryDirectory() as tmpdir:
        out_csv = os.path.join(tmpdir, "train.csv")
        result = module.build_dataset_from_db(limit=20, out_csv=out_csv)

        assert result["rows"] == 2
        assert result["skipped"] == 0
        assert os.path.exists(out_csv)

        df = pd.read_csv(out_csv)
        assert df.shape[0] == 2
        assert "win" in df.columns


def test_train_xgboost_writes_metrics_and_model():
    pytest.importorskip("xgboost")
    module = _load_module(XGB_SCRIPT_PATH, "xgboost_model_module")

    df = pd.DataFrame(
        [
            {"gold_diff": 1000, "kill_diff": 5, "assist_diff": 7, "cs_diff": 30, "vision_diff": 10, "tower_diff": 2, "dragon_diff": 1, "baron_diff": 1, "win": 1},
            {"gold_diff": -800, "kill_diff": -4, "assist_diff": -6, "cs_diff": -20, "vision_diff": -8, "tower_diff": -1, "dragon_diff": -1, "baron_diff": 0, "win": 0},
            {"gold_diff": 900, "kill_diff": 4, "assist_diff": 6, "cs_diff": 24, "vision_diff": 9, "tower_diff": 2, "dragon_diff": 1, "baron_diff": 0, "win": 1},
            {"gold_diff": -700, "kill_diff": -3, "assist_diff": -5, "cs_diff": -18, "vision_diff": -7, "tower_diff": -2, "dragon_diff": -1, "baron_diff": 0, "win": 0},
            {"gold_diff": 1100, "kill_diff": 6, "assist_diff": 8, "cs_diff": 35, "vision_diff": 11, "tower_diff": 3, "dragon_diff": 2, "baron_diff": 1, "win": 1},
            {"gold_diff": -900, "kill_diff": -5, "assist_diff": -7, "cs_diff": -28, "vision_diff": -10, "tower_diff": -2, "dragon_diff": -1, "baron_diff": 0, "win": 0},
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        dataset = os.path.join(tmpdir, "train.csv")
        model_out = os.path.join(tmpdir, "latest_xgb.json")
        metrics_out = os.path.join(tmpdir, "latest_metrics.json")
        df.to_csv(dataset, index=False)

        result = module.train_xgboost(
            dataset_csv=dataset,
            model_out=model_out,
            metrics_out=metrics_out,
            test_size=0.33,
            seed=9,
        )

        assert os.path.exists(model_out)
        assert os.path.exists(metrics_out)
        assert "validation_metrics" in result
        assert "baseline_metrics" in result
        assert "roc_auc" in result["validation_metrics"]
