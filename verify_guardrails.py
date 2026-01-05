import requests
import json
import time

BASE_URL = "http://localhost:5000/api/ask"

def test_query(query, expected_result):
    print(f"\n--- Testing: '{query}' ---")
    try:
        resp = requests.post(BASE_URL, json={"query": query}, timeout=30)
        data = resp.json()
        synthesis = data.get("synthesis", "")
        message = data.get("message", "")
        
        is_blocked = "strictly bound to answer only questions about Microservices" in synthesis or "strictly bound" in message
        
        if expected_result == "BLOCK":
            if is_blocked:
                print(f"[PASS] Correctly Blocked.")
            else:
                 print(f"[FAIL] Allowed (Should Block).")
        elif expected_result == "ALLOW":
            if is_blocked:
                print(f"[FAIL] Blocked (Should Allow).")
            else:
                 print(f"[PASS] Allowed.")
        
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    print("Waiting 2s for auto-reload...")
    time.sleep(2)
    
    # 1. Allowed Queries (Contain Keywords)
    test_query("what is a circuit breaker?", "ALLOW")
    test_query("deploying docker containers", "ALLOW")
    test_query("api gateway patterns", "ALLOW")
    test_query("microservices best practices", "ALLOW")
    
    # 2. Blocked Queries (No Keywords)
    test_query("hi", "BLOCK")
    test_query("how to cook pasta", "BLOCK")
    test_query("tell me about python", "BLOCK") # Generic
    test_query("best database?", "ALLOW") # 'database' is in whitelist, so this is allowed (acceptable trade-off)
    test_query("who is the president", "BLOCK")
