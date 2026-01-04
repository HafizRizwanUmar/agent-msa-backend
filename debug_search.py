
import requests
import json
import time

BASE_URL = "https://api.stackexchange.com/2.3"

def test_search(query):
    print(f"Testing search for: '{query}'")
    
    # 1. Try Specific Search
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": query,
        "tagged": "microservices",
        "site": "stackoverflow",
        "pagesize": 5
    }
    
    headers = {"User-Agent": "AgentMSA-Debug/1.0"}

    print("\n--- Attempt 1: Specific Search (tagged=microservices) ---")
    try:
        resp = requests.get(f"{BASE_URL}/search/advanced", params=params, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Response: {resp.text}")
        data = resp.json()
        items = data.get("items", [])
        print(f"Found {len(items)} items")
        if not items and "error_message" in data:
            print(f"Error: {data['error_message']}")
    except Exception as e:
        print(f"Exception: {e}")
        items = []

    # 2. Try Fallback Search
    if not items:
        print("\n--- Attempt 2: Fallback Search (broad) ---")
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "site": "stackoverflow",
            "pagesize": 5
        }
        try:
            resp = requests.get(f"{BASE_URL}/search/advanced", params=params, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Response: {resp.text}")
            data = resp.json()
            items = data.get("items", [])
            print(f"Found {len(items)} items")
            if not items and "error_message" in data:
                print(f"Error: {data['error_message']}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_search("microservices architecture")
