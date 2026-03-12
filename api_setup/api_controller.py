import os
import requests
import time
from dotenv import load_dotenv
from database_setup.db_manager import save_player

load_dotenv()

class RiotAPIProvider:
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")
        self.region = "americas"
        self.headers = {"X-Riot-Token": self.api_key}
        
        # Safeguard: Validate API Key on initialization
        if not self.api_key:
            raise ValueError("RIOT_API_KEY not found in environment variables.")

    def _make_request(self, url):
        # Internal helper to handle rate limiting
        response = requests.get(url, headers=self.headers)

        if response.status_code == 429:
            # Safeguard: Read 'Retry-After' header or default to 10 seconds
            wait_time = int(response.headers.get("Retry-After", 10))
            print(f"Rate limit hit. Waiting {wait_time}s...")
            time.sleep(wait_time)
            return self._make_request(url)

        return response

    def get_puuid(self, game_name, tag_line):
        url = f"https://{self.region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = self._make_request(url)
        if response.status_code == 200:
            return response.json().get('puuid')
        return None

    def get_match_ids(self, puuid, count=5):
        url = f"https://{self.region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
        response = self._make_request(url)
        if response.status_code == 200:
            return response.json()
        return []

if __name__ == "__main__":
    try:
        provider = RiotAPIProvider()
        game_name = "Dedgurs"
        tag_line = "MEOW"
        
        puuid = provider.get_puuid(game_name, tag_line)
        
        if puuid:
            print(f"PUUID: {puuid}")
            # Link API retrieval to Database storage
            save_player(puuid, game_name) 
            
            matches = provider.get_match_ids(puuid)
            print(f"Matches: {matches}")
    except Exception as e:
        print(f"System Error: {e}")