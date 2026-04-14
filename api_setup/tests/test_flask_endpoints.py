import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api_setup.flask_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def _make_minimal_match(team1_win=True):
    participants = []
    for i in range(10):
        team_id = 100 if i < 5 else 200
        participants.append({
            "teamId": team_id,
            "kills": 3, "assists": 2, "deaths": 1,
            "totalMinionsKilled": 150, "neutralMinionsKilled": 10,
            "visionScore": 20, "goldEarned": 12000,
            "puuid": f"test-puuid-player-{i}"
        })
    return {
        "metadata": {
            "matchId": "NA1-MOCK-001",
            "participants": [f"test-puuid-player-{i}" for i in range(10)]
        },
        "info": {
            "gameCreation": 1700000000000,
            "gameDuration": 1800,
            "participants": participants,
            "teams": [
                {"teamId": 100, "win": team1_win, "objectives": {
                    "tower": {"kills": 5}, "dragon": {"kills": 2}, "baron": {"kills": 1}
                }},
                {"teamId": 200, "win": not team1_win, "objectives": {
                    "tower": {"kills": 3}, "dragon": {"kills": 1}, "baron": {"kills": 0}
                }}
            ]
        }
    }

_MOCK_FEATURES = {
    "gold_diff": 4000, "kill_diff": 8, "assist_diff": 11, "cs_diff": 95,
    "vision_diff": 22, "tower_diff": 2, "dragon_diff": 1, "baron_diff": 1, "win": 1
}

_MOCK_PLAYER_STATS = {
    "summoner_id": "fake-puuid-001",
    "summoner_name": "TestUser",
    "wins": 3,
    "losses": 2,
    "highest_season_tier": None
}


def test_health_returns_200(client):
    """[Functional] /api/health returns 200 and status ok."""
    resp = client.get("/api/health")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["status"] == "ok"
    print(f"  GET /api/health -> {resp.status_code} | response: {data}")


def test_player_lookup_success(client):
    """[Functional] /api/player returns player data with correct win_rate."""
    with patch("api_setup.flask_app.RiotAPIProvider") as MockProvider, \
         patch("api_setup.flask_app.save_player"), \
         patch("api_setup.flask_app.get_player_stats", return_value=_MOCK_PLAYER_STATS):
        MockProvider.return_value.get_puuid.return_value = "fake-puuid-001"
        resp = client.get("/api/player/TestUser/NA1")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["puuid"] == "fake-puuid-001"
    assert data["wins"] == 3
    assert data["losses"] == 2
    assert data["win_rate"] == "60%"
    print(f"  GET /api/player/TestUser/NA1 -> {resp.status_code}")
    print(f"  puuid='{data['puuid']}', wins={data['wins']}, losses={data['losses']}, "
          f"win_rate='{data['win_rate']}' (3/(3+2) = 60%)")


def test_player_lookup_not_found(client):
    """[Functional] /api/player returns 404 when PUUID is not found."""
    with patch("api_setup.flask_app.RiotAPIProvider") as MockProvider:
        MockProvider.return_value.get_puuid.return_value = None
        resp = client.get("/api/player/FakeUser/0000")
    data = resp.get_json()
    assert resp.status_code == 404
    assert "error" in data
    print(f"  GET /api/player/FakeUser/0000 -> {resp.status_code}")
    print(f"  Riot API returned None (player not found) | error: '{data['error']}'")


def test_fetch_matches_success(client):
    """[Functional] /api/matches/fetch stores matches and returns count."""
    with patch("api_setup.flask_app.RiotAPIProvider") as MockProvider:
        MockProvider.return_value.fetch_and_store_matches.return_value = None
        resp = client.post(
            "/api/matches/fetch",
            data=json.dumps({"puuid": "test-puuid-abc", "count": 3}),
            content_type="application/json"
        )
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 3
    assert "Matches fetched" in data["message"]
    print(f"  POST /api/matches/fetch {{puuid: 'test-puuid-abc', count: 3}} -> {resp.status_code}")
    print(f"  message='{data['message']}', count={data['count']}")


def test_fetch_matches_missing_puuid(client):
    """[Security/Validation] /api/matches/fetch returns 400 when puuid is absent."""
    resp = client.post(
        "/api/matches/fetch",
        data=json.dumps({}),
        content_type="application/json"
    )
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["error"] == "puuid is required"
    print(f"  POST /api/matches/fetch {{}} (missing puuid) -> {resp.status_code}")
    print(f"  Validation caught missing field | error: '{data['error']}'")


def test_get_matches_for_player(client):
    """[Functional] /api/matches/<puuid> returns match list from DB."""
    mock_row = {"match_id": "NA1_999", "game_date": None, "game_length": 1500, "winning_team": "100"}
    with patch("api_setup.flask_app.get_matches_for_player", return_value=[mock_row]):
        resp = client.get("/api/matches/test-puuid-abc")
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data["matches"]) == 1
    assert data["matches"][0]["match_id"] == "NA1_999"
    print(f"  GET /api/matches/test-puuid-abc -> {resp.status_code}")
    print(f"  {len(data['matches'])} match(es) returned")
    print(f"  First match: match_id='{data['matches'][0]['match_id']}', "
          f"game_length={data['matches'][0]['game_length']}s")


def test_predict_valid_match(client):
    """[Functional] /api/predict returns probability and features for valid match JSON."""
    mock_booster = MagicMock()
    mock_booster.predict.return_value = np.array([0.87])
    with patch("api_setup.flask_app.extract_team_features", return_value=_MOCK_FEATURES), \
         patch("api_setup.flask_app._get_model", return_value=mock_booster):
        resp = client.post(
            "/api/predict",
            data=json.dumps(_make_minimal_match()),
            content_type="application/json"
        )
    data = resp.get_json()
    assert resp.status_code == 200
    assert 0.0 <= data["team1_win_probability"] <= 1.0
    assert data["predicted_winner"] in ("Team 1", "Team 2")
    assert len(data["features_used"]) == 8
    print(f"  POST /api/predict -> {resp.status_code}")
    print(f"  team1_win_probability={data['team1_win_probability']:.4f}, "
          f"predicted_winner='{data['predicted_winner']}'")
    print(f"  features_used: {data['features_used']}")


def test_predict_invalid_body(client):
    """[Security/Validation] /api/predict returns 400 for malformed match JSON."""
    with patch("api_setup.flask_app.extract_team_features", side_effect=Exception("bad data")):
        resp = client.post(
            "/api/predict",
            data=json.dumps({"garbage": True}),
            content_type="application/json"
        )
    data = resp.get_json()
    assert resp.status_code == 400
    assert "error" in data
    print(f"  POST /api/predict {{garbage: true}} -> {resp.status_code}")
    print(f"  Feature extraction raised exception | error: '{data['error']}'")


def test_predict_from_stored_match(client):
    """[Integration] /api/predict/match/<id> predicts from match stored in DB."""
    raw = json.dumps(_make_minimal_match())
    mock_booster = MagicMock()
    mock_booster.predict.return_value = np.array([0.73])
    with patch("api_setup.flask_app.get_raw_match_json", return_value=raw), \
         patch("api_setup.flask_app.extract_team_features", return_value=_MOCK_FEATURES), \
         patch("api_setup.flask_app._get_model", return_value=mock_booster):
        resp = client.get("/api/predict/match/NA1_TESTMATCH")
    data = resp.get_json()
    assert resp.status_code == 200
    assert "team1_win_probability" in data
    print(f"  GET /api/predict/match/NA1_TESTMATCH -> {resp.status_code}")
    print(f"  Raw JSON fetched from DB, parsed, features extracted, model predicted")
    print(f"  team1_win_probability={data['team1_win_probability']:.4f}, "
          f"predicted_winner='{data['predicted_winner']}'")


def test_predict_from_stored_not_found(client):
    """[Functional] /api/predict/match/<id> returns 404 for unknown match ID."""
    with patch("api_setup.flask_app.get_raw_match_json", return_value=None):
        resp = client.get("/api/predict/match/NONEXISTENT")
    data = resp.get_json()
    assert resp.status_code == 404
    assert data["error"] == "Match not found in database"
    print(f"  GET /api/predict/match/NONEXISTENT -> {resp.status_code}")
    print(f"  DB returned None (no matching row) | error: '{data['error']}'")
