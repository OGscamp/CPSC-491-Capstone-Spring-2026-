import pytest
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database_setup.db_manager import (
    get_db_connection, save_player, save_match_data,
    get_player_stats, get_matches_for_player, get_raw_match_json, get_recent_matches
)

# Minimal valid match JSON that satisfies save_match_data and extract_team_features
def _make_minimal_match(match_id="NA1-RTEST-001", team1_win=True):
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
            "matchId": match_id,
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

PLAYER_IDS = ["test-r1", "test-r2"]
MATCH_IDS = ["NA1-RTEST-001", "NA1-RTEST-002", "NA1-RTEST-003"]

@pytest.fixture(autouse=True)
def cleanup():
    yield
    conn = get_db_connection()
    if conn:
        try:
            conn.rollback()
            cursor = conn.cursor()
            for pid in PLAYER_IDS:
                cursor.execute("DELETE FROM PLAYER WHERE summoner_id = %s", (pid,))
            for mid in MATCH_IDS:
                cursor.execute("DELETE FROM MATCH_DATA WHERE match_id = %s", (mid,))
            conn.commit()
            cursor.close()
        except Exception:
            conn.rollback()
        finally:
            conn.close()


def test_get_player_stats_returns_fields():
    """[Integration] get_player_stats returns correct fields with default values."""
    save_player("test-r1", "R1User")
    result = get_player_stats("test-r1")
    assert result is not None
    assert result["summoner_name"] == "R1User"
    assert result["wins"] == 0
    assert result["losses"] == 0
    print(f"  Queried PUUID: 'test-r1'")
    print(f"  Returned: summoner_name='{result['summoner_name']}', "
          f"wins={result['wins']}, losses={result['losses']}, "
          f"tier={result.get('highest_season_tier')}")


def test_get_player_stats_not_found():
    """[Integration] get_player_stats returns None for unknown PUUID."""
    result = get_player_stats("definitely-does-not-exist-xyz")
    assert result is None
    print(f"  Queried PUUID: 'definitely-does-not-exist-xyz' (not in DB)")
    print(f"  Returned: None — correct, no row exists")


def test_get_raw_match_json_returns_string():
    """[Integration] get_raw_match_json returns raw JSON string containing the match ID."""
    save_match_data(_make_minimal_match("NA1-RTEST-001"))
    raw = get_raw_match_json("NA1-RTEST-001")
    assert raw is not None
    assert isinstance(raw, str)
    assert "NA1-RTEST-001" in raw
    parsed = json.loads(raw)
    print(f"  Queried match_id: 'NA1-RTEST-001'")
    print(f"  Returned: raw JSON string ({len(raw)} chars)")
    print(f"  matchId in parsed JSON: '{parsed['metadata']['matchId']}'")
    print(f"  gameDuration: {parsed['info']['gameDuration']}s")


def test_get_raw_match_json_not_found():
    """[Integration] get_raw_match_json returns None for unknown match ID."""
    result = get_raw_match_json("MATCH-DOES-NOT-EXIST")
    assert result is None
    print(f"  Queried match_id: 'MATCH-DOES-NOT-EXIST' (not in DB)")
    print(f"  Returned: None — correct, no row exists")


def test_get_recent_matches_returns_list():
    """[Integration] get_recent_matches returns a non-empty list with expected keys."""
    save_match_data(_make_minimal_match("NA1-RTEST-002"))
    results = get_recent_matches(limit=5)
    assert isinstance(results, list)
    assert len(results) >= 1
    assert "match_id" in results[0]
    assert "game_length" in results[0]
    assert "winning_team" in results[0]
    print(f"  Inserted match: 'NA1-RTEST-002'")
    print(f"  get_recent_matches(limit=5) returned {len(results)} row(s)")
    print(f"  First row: match_id='{results[0]['match_id']}', "
          f"game_length={results[0]['game_length']}s, "
          f"winning_team={results[0]['winning_team']}")


def test_get_recent_matches_respects_limit():
    """[Integration] get_recent_matches does not return more rows than the limit."""
    for i, mid in enumerate(["NA1-RTEST-001", "NA1-RTEST-002", "NA1-RTEST-003"]):
        save_match_data(_make_minimal_match(mid, team1_win=(i % 2 == 0)))
    results = get_recent_matches(limit=2)
    assert len(results) <= 2
    print(f"  Inserted 3 matches into MATCH_DATA")
    print(f"  get_recent_matches(limit=2) returned {len(results)} row(s) — limit enforced")
    for r in results:
        print(f"    {r['match_id']} | winning_team={r['winning_team']}")
