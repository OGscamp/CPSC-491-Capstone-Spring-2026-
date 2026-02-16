import requests

def test_unauthorized():
    print("--- Running Security Test: Unauthorized Access ---")
    url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Luuser/Meow"
    
    # Intentionally bad key
    headers = {"X-Riot-Token": "RGAPI-FAKE-EXPIRED-KEY"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("SUCCESS: System correctly blocked unauthorized request.")
    else:
        print("FAILED: System allowed or misclassified bad key.")

if __name__ == "__main__":
    test_unauthorized()