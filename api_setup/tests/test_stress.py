import requests
import os
import time
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": API_KEY}
URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Luuser/Meow"

def request_no_safeguard(i):
    return requests.get(URL, headers=HEADERS).status_code

def request_with_safeguard(i):
    # Safeguard: Simple pacing to ensure we don't exceed 20/sec
    time.sleep(i * 0.1) 
    response = requests.get(URL, headers=HEADERS)
    return response.status_code

def run_comparison():
    # PHASE 1: NO SAFEGUARDS
    print("Phase 1: Sending 25 Concurrent Requests (No Safeguards)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        results_fail = list(executor.map(request_no_safeguard, range(25)))
    
    fails = results_fail.count(429)
    print(f"Phase 1 Complete. Successful (200 OK) requests: {results_fail.count(200)}")
    print(f"429 Errors detected: {fails}")

    print("\nPausing for 3 seconds\n")
    time.sleep(5)

    # PHASE 2: WITH SAFEGUARDS
    print("Phase 2: Sending 25 Requests (With Safeguards)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        results_pass = list(executor.map(request_with_safeguard, range(25)))
    
    passes = results_pass.count(200)
    print(f"Phase 2 Complete. Successful (200 OK) requests: {passes}")
    print(f"429 Errors detected: {results_pass.count(429)}")

if __name__ == "__main__":
    run_comparison()