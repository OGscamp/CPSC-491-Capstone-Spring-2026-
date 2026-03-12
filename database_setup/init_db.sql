
CREATE DATABASE IF NOT EXISTS lol_prediction_db;
USE lol_prediction_db;

-- PLAYER Table: Stores unique Riot PUUIDs and basic stats
CREATE TABLE IF NOT EXISTS PLAYER (
    summoner_id VARCHAR(100) PRIMARY KEY,
    summoner_name VARCHAR(45),
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    highest_season_tier VARCHAR(20)
);

-- GAME Table: Stores match history for training
CREATE TABLE IF NOT EXISTS GAME (
    game_id VARCHAR(50) PRIMARY KEY,
    game_date DATETIME,
    game_length INT,
    winning_team CHAR(10)
);