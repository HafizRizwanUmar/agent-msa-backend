
import requests
import re
import html

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext)

def test_scrape(url):
    print(f"Testing scrape for: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Failed with status: {resp.status_code}")
            return

        page_html = resp.text
        clean_page = page_html.replace('\n', ' ')
        
        # Original Logic
        body_parts = re.split(r'class="(?:js-post-body|post-text)"[^>]*>', clean_page)
        print(f"Body parts found: {len(body_parts)}")
        
        if len(body_parts) >= 3:
            raw_answer = body_parts[2].split('</div>')[0]
            print(f"Extracted Answer Preview: {clean_html(raw_answer)[:200]}")
        elif len(body_parts) >= 2:
            raw_q = body_parts[1].split('</div>')[0]
            print(f"Extracted Question Preview: {clean_html(raw_q)[:200]}")
        else:
            print("Failed to find body parts with regex.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with a known SO URL
    test_scrape("https://stackoverflow.com/questions/17573602/how-to-implement-microservices-architecture")
