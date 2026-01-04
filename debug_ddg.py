
import requests
import re

def test_ddg(query):
    # Use the 'lite' HTML version of, which is easier to scrape
    url = "https://html.duckduckgo.com/html/"
    params = {
        "q": f"site:stackoverflow.com {query}"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Testing DuckDuckGo search: {url} with q='{params['q']}'")
    try:
        resp = requests.post(url, data=params, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            # Extract StackOverflow links
            # DDG result links are strictly in <a class="result__a" href="...">
            links = re.findall(r'class="result__a" href="([^"]+)"', resp.text)
            
            # Filter for actual stackoverflow question links
            so_links = [l for l in links if "stackoverflow.com/questions/" in l]
            
            print(f"Found {len(so_links)} SO links:")
            for l in so_links[:5]:
                print(f"- {l}")
                
            if not so_links:
                print("No SO links found. Snippet:")
                print(resp.text[:500])
        else:
            print(f"Blocked? Status: {resp.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_ddg("what are microservices")
