
import requests
from bs4 import BeautifulSoup
import time

def test_scrape_bs4(url):
    print(f"Testing scrape (BS4) for: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Failed with status: {resp.status_code}")
            return

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Strategy: Look for the accepted answer first, then any answer
        # Stack Overflow typically puts the accepted answer in a div with class 'accepted-answer' or just looks for the vote count
        
        # Modern SO structure:
        # Question body: <div class="js-post-body" itemprop="text">
        # Answers: <div class="js-post-body" itemprop="text"> associated with answer divs
        
        post_bodies = soup.find_all(class_="js-post-body")
        print(f"Post bodies found: {len(post_bodies)}")
        
        if len(post_bodies) >= 2:
            # Index 0 is question, Index 1 is first answer (usually accepted or highest rated)
            print("--- Question Snippet ---")
            print(post_bodies[0].get_text(strip=True)[:200])
            print("\n--- Answer Snippet ---")
            print(post_bodies[1].get_text(strip=True)[:200])
        elif len(post_bodies) == 1:
            print("--- Question Snippet (No answers found) ---")
            print(post_bodies[0].get_text(strip=True)[:200])
        else:
            print("No post bodies found. Page structure might be different.")
            # Fallback debug
            print("Snippet:", soup.prettify()[:500])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape_bs4("https://stackoverflow.com/questions/17573602/how-to-implement-microservices-architecture")
