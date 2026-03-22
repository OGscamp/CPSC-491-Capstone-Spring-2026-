import os
import sys

THIS_DIR = os.path.dirname(__file__)
ML_SCRIPTS_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "ML Scripts"))
sys.path.append(ML_SCRIPTS_DIR)

from feature_engineering import extract_team_features

def test_feature_extraction_valid():
    sample = {
        "info": {
            "participants": [{
                "kills": 5,
                "assists": 7,
                "goldEarned": 12000,
                "totalMinionsKilled": 150,
                "neutralMinionsKilled": 10,
                "visionScore": 20
            }] * 10,
            "teams": [
                {
                    "teamId": 100,
                    "win": True,
                    "objectives": {
                        "tower": {"kills": 5},
                        "dragon": {"kills": 2},
                        "baron": {"kills": 1},
                    },
                },
                {
                    "teamId": 200,
                    "win": False,
                    "objectives": {
                        "tower": {"kills": 3},
                        "dragon": {"kills": 1},
                        "baron": {"kills": 0},
                    },
                },
            ],
        }
    }

    features = extract_team_features(sample)
    assert "kill_diff" in features
    assert "win" in features
