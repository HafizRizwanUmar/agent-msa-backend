
import requests
import re

def test_provider(name, url, params, headers):
    print(f"\n--- Testing {name} ---")
    print(f"URL: {url}")
    try:
        if "duckduckgo" in url:
             resp = requests.post(url, data=params, headers=headers, timeout=10)
        else:
             resp = requests.get(url, params=params, headers=headers, timeout=10)
             
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Content Length: {len(resp.text)}")
            if "stackoverflow.com" in resp.text:
                print("SUCCESS: Found StackOverflow link in text.")
            else:
                print("WARNING: No StackOverflow link found (might be captcha or empty).")
        else:
            print(f"FAILED: Status {resp.status_code}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

def main():
    query = "site:stackoverflow.com microservices"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 1. DDG HTML
    test_provider("DDG HTML", "https://html.duckduckgo.com/html/", {"q": query}, headers)

    # 2. DDG Lite
    test_provider("DDG Lite", "https://lite.duckduckgo.com/lite/", {"q": query}, headers)
    
    # 3. StackOverflow Direct (Broad)
    test_provider("SO Direct", "https://stackoverflow.com/search", {"q": "microservices"}, headers)

if __name__ == "__main__":
    main()
