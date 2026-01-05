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
            # Check for synthesis or specific refusal message
            synthesis = data.get("synthesis", "")
            message = data.get("message", "")
            results = data.get("results", [])
            
            print(f"Response Synthesis: {synthesis[:100]}...")
            print(f"Response Message: {message}")
            print(f"Results Count: {len(results)}")
            
            if "bound to answer only questions about microservices" in synthesis or "bound to answer only questions about microservices" in message:
                print("[PASS] Correctly Refused.")
            elif len(results) > 0:
                print("[PASS] Got Results (Allowed).")
            else:
                 print("[INFO] No results (Ambiguous or valid empty)")
        else:
            print(f"[ERROR] Error: {resp.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    print("Waiting 2s for auto-reload...")
    time.sleep(2)
    
    # 1. Allowed Topic
    test_query("microservices patterns", "Valid Microservices Question")
    
    # 2. Ignored Topic
    test_query("how to cook pasta", "Invalid Random Question")
    
    # 3. Ambiguous Topic (might match if lucky, likely refuse)
    test_query("what is the capital of france", "Invalid Fact Question")
