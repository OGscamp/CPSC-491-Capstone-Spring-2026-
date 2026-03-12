import mysql.connector
import os
from dotenv import load_dotenv

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
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized: Tables verified/created.")

if __name__ == "__main__":
    initialize_db()