import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="lol_prediction_db",
            auth_plugin='mysql_native_password' 
        )
        return connection
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def save_player(puuid, summoner_name):
    # Implements the basic flow of data storage
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = "INSERT IGNORE INTO PLAYER (summoner_id, summoner_name) VALUES (%s, %s)"
        cursor.execute(sql, (puuid, summoner_name))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Saved {summoner_name} to database.")

def initialize_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Create PLAYER table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PLAYER (
                summoner_id VARCHAR(100) PRIMARY KEY,
                summoner_name VARCHAR(45),
                wins INT DEFAULT 0,
                losses INT DEFAULT 0,
                highest_season_tier VARCHAR(20)
            )
        """)
        # Create GAME table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GAME (
                game_id VARCHAR(50) PRIMARY KEY,
                game_date DATETIME,
                game_length INT,
                winning_team CHAR(10)
            )
        """)
        # Create MATCH_DATA table for raw JSON storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS MATCH_DATA (
                match_id VARCHAR(50) PRIMARY KEY,
                game_date DATETIME,
                game_length INT,
                winning_team CHAR(10),
                raw_json LONGTEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized: Tables verified/created.")

def save_match_data(match_json):
    # Stores raw match JSON plus core summary fields for ML training
    if not match_json:
        return

    metadata = match_json.get("metadata", {})
    info = match_json.get("info", {})

    match_id = metadata.get("matchId")
    if not match_id:
        return

    # Convert milliseconds to datetime if present
    game_creation_ms = info.get("gameCreation")
    game_date = None
    if game_creation_ms:
        game_date = datetime.utcfromtimestamp(game_creation_ms / 1000)

    game_length = info.get("gameDuration")
    winning_team = None
    teams = info.get("teams", [])
    for team in teams:
        if team.get("win"):
            winning_team = str(team.get("teamId"))
            break

    raw_json = json.dumps(match_json)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT IGNORE INTO MATCH_DATA (match_id, game_date, game_length, winning_team, raw_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (match_id, game_date, game_length, winning_team, raw_json),
        )
        cursor.execute(
            """
            INSERT IGNORE INTO GAME (game_id, game_date, game_length, winning_team)
            VALUES (%s, %s, %s, %s)
            """,
            (match_id, game_date, game_length, winning_team),
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Saved match {match_id} to database.")

if __name__ == "__main__":
    initialize_db()
