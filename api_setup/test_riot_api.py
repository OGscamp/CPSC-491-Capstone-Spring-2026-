import os
import requests
from dotenv import load_dotenv

# Load API key from env file
load_dotenv()

def test_connection():
    api_key = os.getenv("RIOT_API_KEY")
    region = "americas" 

    game_name = "Luuser"
    tag_line = "Meow"

    print(f"--- API Test for {game_name}#{tag_line} ---")

    # STEP 1: Get PUUID (Account-V1)
    account_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": api_key}
    
    acc_response = requests.get(account_url, headers=headers)
    
    if acc_response.status_code == 200:
        puuid = acc_response.json()['puuid']
        print(f"PUUID retrieved: {puuid}")
        
        # STEP 2: Get Match History (Match-V5) (Getting last 5)
        match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=5"
        match_response = requests.get(match_url, headers=headers)
        
        if match_response.status_code == 200:
            print(f"Recent 5 Match IDs: {match_response.json()}")
        else:
            print(f"Match API failed with status: {match_response.status_code}")
    else:
        print(f"Account API failed. Status: {acc_response.status_code}")

if __name__ == "__main__":
    test_connection()