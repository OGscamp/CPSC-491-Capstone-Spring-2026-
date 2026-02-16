import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    api_key = os.getenv("RIOT_API_KEY")
    region = "americas" 
    game_name = "Luuser"
    tag_line = "Meow"
    headers = {"X-Riot-Token": api_key}

    print(f"--- Running Functional Test: {game_name}#{tag_line} ---")

    # STEP 1: Get PUUID
    account_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    acc_response = requests.get(account_url, headers=headers)
    
    if acc_response.status_code != 200:
        print(f"FAILED: Account API status {acc_response.status_code}")
        return False

    puuid = acc_response.json().get('puuid')
    print(f"PUUID retrieved: {puuid}")
    
    # STEP 2: Get Match History
    match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=5"
    match_response = requests.get(match_url, headers=headers)
    
    if match_response.status_code == 200:
        print(f"SUCCESS: Recent Match IDs found.")
        return True
    else:
        print(f"FAILED: Match API status {match_response.status_code}")
        return False

if __name__ == "__main__":
    test_connection()