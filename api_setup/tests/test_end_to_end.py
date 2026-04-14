import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api_setup.flask_app import app
from database_setup.db_manager import get_db_connection, save_player, save_match_data

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../projects/tests/output/xgb_model.json')
)


def _db_available():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            conn.close()
            return True
    except Exception:
        pass
    return False


DB_AVAILABLE = _db_available()
MODEL_EXISTS = os.path.exists(MODEL_PATH)

E2E_PLAYER_IDS = ["e2e-puuid-001"]
E2E_MATCH_IDS  = ["NA1-E2E-001", "NA1-E2E-002"]


def _make_e2e_match(match_id="NA1-E2E-001", team1_win=True):
    participants = []
    for i in range(10):
        team_id = 100 if i < 5 else 200
        participants.append({
            "teamId": team_id,
            "kills": 3, "assists": 2, "deaths": 1,
            "totalMinionsKilled": 150, "neutralMinionsKilled": 10,
            "visionScore": 20, "goldEarned": 12000,
            "puuid": "e2e-puuid-001" if i == 0 else f"other-puuid-{i}"
        })
    return {
        "metadata": {
            "matchId": match_id,
            "participants": ["e2e-puuid-001"] + [f"other-puuid-{i}" for i in range(1, 10)]
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


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if not DB_AVAILABLE:
        return
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        for mid in E2E_MATCH_IDS:
            cursor.execute("DELETE FROM MATCH_DATA WHERE match_id = %s", (mid,))
            cursor.execute("DELETE FROM GAME WHERE game_id = %s", (mid,))
        for pid in E2E_PLAYER_IDS:
            cursor.execute("DELETE FROM PLAYER WHERE summoner_id = %s", (pid,))
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_health_no_mocks(client):
    """[E2E] Flask test client works with zero mocking — canary test."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


@pytest.mark.skipif(not MODEL_EXISTS, reason="xgb_model.json not found")
def test_predict_post_with_real_model(client):
    """[E2E] POST /api/predict runs through the real XGBoost model with no DB dependency."""
    resp = client.post(
        "/api/predict",
        data=json.dumps(_make_e2e_match()),
        content_type="application/json"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert 0.0 <= data["team1_win_probability"] <= 1.0
    assert data["predicted_winner"] in ("Team 1", "Team 2")
    assert len(data["features_used"]) == 8


@pytest.mark.skipif(not DB_AVAILABLE or not MODEL_EXISTS,
                    reason="MySQL or xgb_model.json unavailable")
def test_predict_from_db_full_stack(client):
    """[E2E] Core path: save_match_data → GET /api/predict/match/<id> → real DB + real model."""
    save_match_data(_make_e2e_match("NA1-E2E-001"))
    resp = client.get("/api/predict/match/NA1-E2E-001")
    assert resp.status_code == 200
    data = resp.get_json()
    assert 0.0 <= data["team1_win_probability"] <= 1.0
    assert data["predicted_winner"] in ("Team 1", "Team 2")
    assert len(data["features_used"]) == 8


@pytest.mark.skipif(not DB_AVAILABLE, reason="MySQL unavailable")
def test_predict_from_db_not_found(client):
    """[E2E] GET /api/predict/match/<id> returns 404 via real DB when match does not exist."""
    resp = client.get("/api/predict/match/NA1-E2E-NONEXISTENT")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Match not found in database"


@pytest.mark.skipif(not DB_AVAILABLE, reason="MySQL unavailable")
def test_get_matches_after_save(client):
    """[E2E] save_player + save_match_data → GET /api/matches/<puuid> returns real DB data."""
    save_player("e2e-puuid-001", "E2EUser")
    save_match_data(_make_e2e_match("NA1-E2E-001"))
    resp = client.get("/api/matches/e2e-puuid-001")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["puuid"] == "e2e-puuid-001"
    assert len(data["matches"]) >= 1
    assert data["matches"][0]["match_id"] == "NA1-E2E-001"
    assert data["matches"][0]["game_length"] == 1800


@pytest.mark.skipif(not DB_AVAILABLE or not MODEL_EXISTS,
                    reason="MySQL or xgb_model.json unavailable")
def test_predict_from_db_team2_win(client):
    """[E2E] Second distinct match row (team2 win) runs through full stack without error."""
    save_match_data(_make_e2e_match("NA1-E2E-002", team1_win=False))
    resp = client.get("/api/predict/match/NA1-E2E-002")
    assert resp.status_code == 200
    data = resp.get_json()
    prob = data["team1_win_probability"]
    assert 0.0 <= prob <= 1.0
    expected_winner = "Team 1" if prob >= 0.5 else "Team 2"
    assert data["predicted_winner"] == expected_winner
