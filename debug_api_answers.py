
import requests
import json

def test_get_answers():
    # 1. Search for a question first
    print("Searching for a question...")
    search_url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": "microservices authentication",
        "site": "stackoverflow",
        "pagesize": 1
    }
    
    try:
        resp = requests.get(search_url, params=params)
        data = resp.json()
        items = data.get("items", [])
        if not items:
            print("No questions found.")
            return
            
        qid = items[0]["question_id"]
        title = items[0]["title"]
        print(f"Found Question: {title} (ID: {qid})")
        
        # 2. Get Answers for this question
        # Filter '!nNPvSNPH.z' is often used for body, but let's try standard 'withbody' built-in or construct one.
        # Valid filters: 'default', 'withbody' (if available), or custom.
        # Let's try to just get answers endpoint with filter='withbody'.
        
        print(f"Fetching answers for QID {qid}...")
        answers_url = f"https://api.stackexchange.com/2.3/questions/{qid}/answers"
        a_params = {
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "filter": "withbody" # This includes the 'body' field
        }
        
        a_resp = requests.get(answers_url, params=a_params)
        a_data = a_resp.json()
        answers = a_data.get("items", [])
        
        print(f"Found {len(answers)} answers.")
        
        if answers:
            top = answers[0]
            print("\nTop Answer Details:")
            print(f"Score: {top.get('score')}")
            print(f"Is Accepted: {top.get('is_accepted')}")
            print(f"Author Rep: {top.get('owner', {}).get('reputation')}")
            print(f"Body Preview: {top.get('body')[:200]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_get_answers()
