import requests
import json
import time

BASE_URL = "http://localhost:5000/api/ask"

def test_query(query, description):
    print(f"\n--- Testing: {description} ---")
    print(f"Query: '{query}'")
    try:
        start = time.time()
        resp = requests.post(BASE_URL, json={"query": query}, timeout=30)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            synthesis = data.get("synthesis", "")
            message = data.get("message", "")
            results = data.get("results", [])
            
            print(f"Response Message: {message}")
            print(f"Results Count: {len(results)}")
            
            if "bound to answer only questions about microservices" in synthesis or "bound to answer only questions about microservices" in message:
                print("[PASS] Correctly Refused (No Hallucination).")
            elif len(results) > 0 and query == "hi":
                 print("[FAIL] Got Results for 'hi' (Still Hallucinating).")
            elif len(results) > 0:
                 print("[PASS] Got Results (Correctly found).")
            else:
                 print("[INFO] No results.")
        else:
            print(f"[ERROR] Error: {resp.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    print("Waiting 2s for auto-reload...")
    time.sleep(2)
    
    # 1. The Problematic Query
    test_query("hi", "Hallucination Test ('hi')")
    
    # 2. Valid Query
    test_query("microservices patterns", "Valid Question")
