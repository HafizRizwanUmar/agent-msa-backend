
import requests
import re

def test_search_scrape(query):
    url = f"https://stackoverflow.com/search?q={query}&tab=relevance"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Testing search scrape: {url}")
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            print("Search page loaded.")
            # Simple regex to find question links
            # Pattern: <a href="/questions/12345/title" class="s-link">
            links = re.findall(r'href="/questions/(\d+)/[^"]+" class="s-link', resp.text)
            print(f"Found {len(links)} question IDs: {links[:5]}")
            
            if not links:
                print("Warning: No links found via regex. Structure might have changed.")
                print("Snippet:", resp.text[:500])
        else:
            print(f"Blocked? Status: {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_search_scrape("microservices")
