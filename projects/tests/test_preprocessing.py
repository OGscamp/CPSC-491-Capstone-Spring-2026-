from ml.preprocess import extract_features

def test_feature_extraction_valid():
    sample = {
        "participants": [{
            "kills": 5,
            "deaths": 2,
            "assists": 7,
            "goldEarned": 12000,
            "visionScore": 20,
            "damageDealt": 25000,
            "win": True
        }]
    }

    df = extract_features(sample)
    assert df.shape[0] == 1
    assert "kills" in df.columns
