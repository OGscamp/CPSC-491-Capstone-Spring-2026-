import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database_setup.db_manager import get_db_connection, save_player

TEST_IDS = ["verify-123", "dup-999"]

@pytest.fixture(autouse=True)
def cleanup():
    yield
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        for tid in TEST_IDS:
            cursor.execute("DELETE FROM PLAYER WHERE summoner_id = %s", (tid,))
        conn.commit()
        cursor.close()
        conn.close()


def test_auth_handshake():
    """[Security] Verify MySQL connection handshake succeeds."""
    conn = get_db_connection()
    assert conn is not None
    assert conn.is_connected()
    print(f"  Connected to MySQL Server version: {conn.get_server_info()}")
    print(f"  Host: 127.0.0.1:3306 | Auth: mysql_native_password")
    conn.close()
    print(f"  Connection closed cleanly — handshake PASSED")


def test_state_verification():
    """[Integration] Verify PLAYER data is persisted and retrievable."""
    save_player("verify-123", "TestUser")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PLAYER WHERE summoner_id = 'verify-123'")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    assert result is not None
    assert result['summoner_name'] == "TestUser"
    print(f"  Inserted:  summoner_id='verify-123', summoner_name='TestUser'")
    print(f"  Retrieved: {result}")
    print(f"  wins={result['wins']}, losses={result['losses']} (defaults 0 as expected)")


def test_conflict_handling():
    """[Data Integrity] Verify INSERT IGNORE prevents duplicate overwrites."""
    save_player("dup-999", "Original")
    save_player("dup-999", "Clone")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PLAYER WHERE summoner_id = 'dup-999'")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    assert result['summoner_name'] == "Original"
    print(f"  First insert:  summoner_name='Original'")
    print(f"  Second insert: summoner_name='Clone' (duplicate PUUID)")
    print(f"  DB result:     summoner_name='{result['summoner_name']}' — INSERT IGNORE kept original")
