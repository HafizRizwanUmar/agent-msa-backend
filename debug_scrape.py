
import requests

def test_scrape():
    url = "https://stackoverflow.com/questions/11703615/microservices-architecture-what-is-it"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Testing direct scrape of: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Success! We can access the page content directly.")
            print(f"Content length: {len(resp.text)}")
            if "Microservices" in resp.text:
                print("Verified: Content contains expected text.")
        else:
            print(f"Blocked? Status: {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_scrape()
