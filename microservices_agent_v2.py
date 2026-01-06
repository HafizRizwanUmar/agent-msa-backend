import requests
import html
import re
import time
import os
import datetime
from datetime import datetime
from rank_bm25 import BM25Okapi

# Optional ML Imports (Lite Mode for Vercel)
try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    print("Notice: SBERT not available. Running in Lite Mode.")

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class AgentMSA:
    BASE_URL = "https://api.stackexchange.com/2.3"
    
    def __init__(self):
        # 1. Initialize Firebase Admin (Knowledge Base)
        self.db = None
        try:
            if not firebase_admin._apps:
                # Check for Environment Variable (Production/Vercel)
                if os.environ.get("FIREBASE_CREDENTIALS"):
                    import json
                    cred_dict = json.loads(os.environ.get("FIREBASE_CREDENTIALS"))
                    cred = credentials.Certificate(cred_dict)
                # Check for Local File (Development)
                elif os.path.exists("serviceAccountKey.json"):
                    cred = credentials.Certificate("serviceAccountKey.json")
                else:
                    raise FileNotFoundError("No serviceAccountKey.json or FIREBASE_CREDENTIALS found.")
                
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("Knowledge Base (Firestore) connected.")
        except Exception as e:
            print(f"Warning: Could not connect to Knowledge Base: {e}")

        # 2. Local AI Setup
        if SBERT_AVAILABLE:
            print("Loading SBERT model...")
            try:
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
                print("SBERT model loaded.")
            except Exception as e:
                print(f"Warning: Could not load SBERT model: {e}")
                self.encoder = None
        else:
             print("SBERT disabled (Lite Mode).")
             self.encoder = None
            
        # Network Setup
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AgentMSA-Research/1.0 (Educational)"
        })

    # STRICT DOMAIN GUARDRAILS
    DOMAIN_KEYWORDS = {
        # Core Architecture
        "microservice", "microservices", "monolith", "monolithic", "distributed", "architecture", "soa",
        "service", "services", "backend", "frontend", "api", "apis", "endpoint", "rest", "graphql", "grpc",
        
        # Communication & pattern
        "gateway", "proxy", "load balancer", "service discovery", "circuit breaker", "bulkhead", "retry",
        "sidecar", "mesh", "istio", "envoy", "consul", "eureka", "rabbitmq", "kafka", "queue", "topic",
        "event", "event-driven", "messaging", "async", "synchronous", "sagas", "cqrs", "event sourcing",
        
        # Infrastructure & DevOps
        "docker", "container", "containers", "kubernetes", "k8s", "pod", "node", "cluster", "orchestration",
        "helm", "deployment", "scaling", "scalability", "autoscaling", "replica", "cloud", "aws", "azure", 
        "gcp", "serverless", "lambda", "observability", "monitoring", "logging", "tracing", "prometheus", 
        "grafana", "jaeger", "zipkin", "elk", "manager", "worker",
        
        # Concepts
        "latency", "throughput", "resilience", "fault tolerance", "availability", "consistency", "cap theorem",
        "database", "db", "sql", "nosql", "polyglot", "persistence", "transaction", "isolation", "stateful", 
        "stateless", "auth", "authentication", "authorization", "oauth", "jwt", "token", "security",
        "upstream", "downstream", "workflow", "orchestrator", "choreography", "pattern", "practices", "best practices"
    }

    def validate_intent(self, query):
        """Strictly validate if the query belongs to the microservices domain using Gemini."""
        # 0. Quick local check to save tokens and latency for greetings
        if self.is_greeting(query):
            print(f"DEBUG: Query '{query}' identified as greeting. Allowing.")
            return True
        
        return self.validate_with_gemini(query)

    def is_greeting(self, query):
        """Check if the query is a simple greeting or conversational phrase."""
        greetings = {
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening",
            "how are you", "how are you doing", "what's up", "yo", "test"
        }
        # Check exact lower match or if it starts with a greeting (roughly)
        q_clean = query.strip().lower()
        # Remove punctuation
        q_clean = re.sub(r'[^\w\s]', '', q_clean)
        
        if q_clean in greetings:
            return True
            
        return False

    def validate_with_gemini(self, query):
        """Use Google Gemini API to classify the query."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("DEBUG: No GEMINI_API_KEY found. Falling back to keyword match.")
            return self._validate_keywords_fallback(query)
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = (f"You are a strict classifier for a Microservices Assistant.\n"
                  f"Query: '{query}'\n"
                  f"Is this query related to Microservices Architecture, Software Engineering, System Design, DevOps, or Cloud Infrastructure? "
                  f"Even simple greetings like 'hi' or 'hello' should be valid to start a conversation.\n"
                  f"Respond strictly with 'YES' or 'NO'.")
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Extract text
                # Structure: candidates[0].content.parts[0].text
                try:
                    answer = data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                    print(f"DEBUG: Gemini Validation for '{query}': {answer}")
                    if "YES" in answer:
                        return True
                    else:
                        return False
                except (KeyError, IndexError):
                    print("DEBUG: Unexpected Gemini response format.")
                    return self._validate_keywords_fallback(query)
            else:
                print(f"DEBUG: Gemini API Error {response.status_code}: {response.text}")
                return self._validate_keywords_fallback(query)
        except Exception as e:
            print(f"DEBUG: Gemini connection failed: {e}")
            return self._validate_keywords_fallback(query)

    def _validate_keywords_fallback(self, query):
        """Legacy keyword validation as fallback."""
        query_lower = query.lower()
        if query_lower in ["hi", "hello", "hey", "test"]: return True

        # 1. Check for whole word matches against the whitelist
        clean_query = re.sub(r'[^\w\s]', ' ', query_lower)
        query_words = set(clean_query.split())
        
        if not query_words.isdisjoint(self.DOMAIN_KEYWORDS):
            return True
            
        for kw in self.DOMAIN_KEYWORDS:
            if " " in kw and kw in query_lower:
                return True
                
        return False

    def clean_html(self, raw_html):
        """Remove HTML tags and unescape entities."""
        if not raw_html: return ""
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return html.unescape(cleantext)

    def index_knowledge(self, candidate):
        """Save verified (Accepted) answers to the Knowledge Base (Firestore)."""
        if not self.db or not candidate.get('is_accepted'):
            return

        try:
            doc_ref = self.db.collection('knowledge_base').document(str(candidate['question_id']))
            doc = doc_ref.get()
            
            # Only save if it's new or we are updating an old entry
            if not doc.exists:
                print(f"DEBUG: Indexing new verified knowledge: {candidate['title']}")
                doc_ref.set({
                    'id': str(candidate['question_id']),
                    'title': candidate['title'],
                    'content': candidate['answer_text'],
                    'link': candidate['link'],
                    'score': candidate['score'],
                    'reputation': candidate['reputation'],
                    'tags': ['microservices', 'verified'],
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
        except Exception as e:
            print(f"Error indexing knowledge: {e}")

    def search_knowledge_base(self, query):
        """Search the local Knowledge Base first."""
        if not self.db: return []
        
        print(f"DEBUG: Searching Knowledge Base for '{query}'...")
        results = []
        try:
            # Simple retrieval for now - in a real production system we'd use vector search here too.
            # For this prototype, we'll fetch recent verified answers.
            # Note: Firestore doesn't support full-text search natively without extensions (Algolia/Typesense).
            # So we will rely on the fact that if we have seen it, it's "Indexed".
            # For the thesis "Search first" requirement, we can check if we have exact keyword matches in titles
            # or just return a set of "Recommended / Verified" answers if they match tags.
            
            # MVP: Check if we have any documents with titles containing keywords
            # This is client-side filtering which is okay for a prototype size DB.
            docs = self.db.collection('knowledge_base').limit(50).stream()
            
            query_parts = set(re.findall(r'\w+', query.lower()))
            
            for doc in docs:
                data = doc.to_dict()
                title_lower = data.get('title', '').lower()
                title_parts = set(re.findall(r'\w+', title_lower))
                
                # Strict Set Intersection Match
                # "hi" -> {"hi"} ... "architecture" -> {"architecture"} -> intersection is empty.
                common = query_parts.intersection(title_parts)
                
                matches = len(common)
                # require at least 50% match of query words or 2 keywords
                if matches >= 2 or (len(query_parts) > 0 and matches == len(query_parts)):
                    results.append({
                        "title": data.get('title'),
                        "answer_text": data.get('content'),
                        "link": data.get('link'),
                        "score": data.get('score'),
                        "is_accepted": True, # It's in KB, so it's verified
                        "reputation": data.get('reputation'),
                        "hybrid_score": 1.0, # High confidence
                        "creation_date": time.time(), # Mock for now
                        "source_type": "Knowledge Base"
                    })
                    
            if results:
                print(f"DEBUG: Found {len(results)} matches in Knowledge Base.")
                
        except Exception as e:
            print(f"Error searching KB: {e}")
            
        return results

    def search_questions(self, query):
        """Search Stack Overflow via official API using specialized tags."""
        print(f"DEBUG: Searching API for '{query}'...")
        
        # 1. Try Specific Search with Microservices Tag
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "tagged": "microservices",
            "site": "stackoverflow",
            "pagesize": 5
        }
        
        try:
            resp = self.session.get(f"{self.BASE_URL}/search/advanced", params=params, timeout=10)
            data = resp.json()
            items = data.get("items", [])
            
            # 2. Fallback: Broad Search REMOVED to restrict scope
            # if not items:
            #     print("DEBUG: No tagged results, trying broad search...")
            #     params.pop("tagged")
            #     resp = self.session.get(f"{self.BASE_URL}/search/advanced", params=params, timeout=10)
            #     data = resp.json()
            #     items = data.get("items", [])
            
            print(f"DEBUG: Found {len(items)} questions.")
            return items 
            
        except Exception as e:
            print(f"ERROR: Search API failed: {e}")
            return []

    def fetch_answers(self, questions):
        """Fetch answers for the found questions in batch."""
        if not questions: return []
        
        question_ids = [str(q['question_id']) for q in questions]
        ids_str = ";".join(question_ids)
        
        print(f"DEBUG: Fetching answers for QIDs: {ids_str}")
        
        try:
            # Batch fetch answers with body
            url = f"{self.BASE_URL}/questions/{ids_str}/answers"
            params = {
                "order": "desc",
                "sort": "votes",
                "site": "stackoverflow",
                "filter": "withbody", # Critical: Get the answer content
                "pagesize": 15 # Get top 3 per question roughly
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            answers = data.get("items", [])
            
            # Map answers to their parent questions (for title/link context)
            q_map = {q['question_id']: q for q in questions}
            
            candidates = []
            for ans in answers:
                qid = ans.get('question_id')
                parent = q_map.get(qid)
                if not parent: continue
                
                candidates.append({
                    "question_id": qid,
                    "answer_id": ans.get('answer_id'),
                    "title": parent.get('title', 'Unknown'),
                    "link": ans.get('link') or parent.get('link'),
                    "answer_text": self.clean_html(ans.get('body', '')),
                    "raw_html": ans.get('body', ''), # Keep for potential rendering
                    "score": ans.get('score', 0),
                    "is_accepted": ans.get('is_accepted', False),
                    "reputation": ans.get('owner', {}).get('reputation', 0),
                    "creation_date": ans.get('creation_date', time.time()),
                    "source_type": "Live API"
                })
                
            print(f"DEBUG: Retrieved {len(candidates)} answers.")
            return candidates
            
        except Exception as e:
            print(f"ERROR: Answer API failed: {e}")
            return []

    def rank_candidates(self, query, candidates):
        if not candidates: return []
        print(f"DEBUG: Ranking {len(candidates)} candidates...")
        
        # 1. Stack Exchange Signal Score (Vote + Rep + Recency + Accepted)
        for cand in candidates:
             # Normalize Metrics
             vote_score = min(cand["score"] / 50.0, 1.0) # Cap at 50 votes
             rep_score = min(cand["reputation"] / 5000.0, 1.0) # Cap at 5k rep
             
             age_seconds = time.time() - cand["creation_date"]
             recency_score = max(0, 1.0 - (age_seconds / (365 * 24 * 3600 * 3))) # 3 year decay
             
             # Composite Signal Score
             cand["se_score"] = (vote_score * 0.45) + (rep_score * 0.25) + (recency_score * 0.1)
             if cand["is_accepted"]: 
                 cand["se_score"] += 0.20 # Bonus for accepted
                 
             # Bonus for Knowledge Base sources
             if cand.get("source_type") == "Knowledge Base":
                 cand["se_score"] += 0.3
        
        # 2. Semantic Search (SBERT)
        if self.encoder:
            docs = [c["answer_text"] for c in candidates]
            if docs:
                query_emb = self.encoder.encode(query, convert_to_tensor=True)
                doc_embs = self.encoder.encode(docs, convert_to_tensor=True)
                cosine_scores = util.cos_sim(query_emb, doc_embs)[0]
            else:
                cosine_scores = []
        else:
            cosine_scores = [0.0] * len(candidates)
        
        # 3. Keyword Search (BM25)
        if candidates:
            # Tokenize the answer text for each candidate
            bm25 = BM25Okapi([d["answer_text"].split(" ") for d in candidates])
            tokenized_query = query.split(" ")
            bm25_scores = bm25.get_scores(tokenized_query)
            # Normalize BM25
            max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 and max(bm25_scores) > 0 else 1.0
            normalized_bm25 = [s / max_bm25 for s in bm25_scores]
        else:
            normalized_bm25 = []

        # Combine Scores
        for idx, cand in enumerate(candidates):
            sbert_score = float(cosine_scores[idx]) if idx < len(cosine_scores) else 0
            bm25_s = normalized_bm25[idx] if idx < len(normalized_bm25) else 0
            
            # Hybrid Weighting Config (Adjustable)
            if self.encoder:
                # 30% Signal (Trust), 50% Semantic (Meaning), 20% Keyword (Precision)
                cand["hybrid_score"] = (cand["se_score"] * 0.3) + (sbert_score * 0.5) + (bm25_s * 0.2)
            else:
                # Fallback: 50% Signal, 50% Keywords
                cand["hybrid_score"] = (cand["se_score"] * 0.5) + (0) + (bm25_s * 0.5)
            
        candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return candidates[:5] # Return top 5

    def generate_verified_answer(self, query, top_candidates):
        if not top_candidates:
            return "No verified information found in the knowledge base."
        
        # For now, we take the best answer and check if we can summarize it or present it beautifully.
        # Ideally, an LLM would synthesize this. Since we don't have an LLM key active in this logic,
        # we will structure the output for the frontend to render nicely.
        
        best = top_candidates[0]
        
        synthesis = f"### Top Verified Solution\n\n"
        synthesis += f"**Context**: {best['title']}\n"
        if best.get('source_type') == "Knowledge Base":
             synthesis += f"**Source**: 🏛️ Knowledge Base (Indexed)\n"
        else:
             synthesis += f"**Source**: ☁️ Live Stack Overflow\n"
             
        synthesis += f"**Confidence**: {best['hybrid_score']:.2f} (Votes: {best['score']}, Rep: {best['reputation']})\n\n"
        synthesis += f"{best['answer_text'][:1500]}\n" # Truncate for safety
        
        if len(best['answer_text']) > 1500:
            synthesis += "\n\n*(Answer truncated for brevity. Click source to read full detail)*"

        return synthesis

    def ask(self, user_query):
        print(f"AgentMSA: Processing query '{user_query}'...")
        
        # 0. Check for Greeting First
        if self.is_greeting(user_query):
             return {
                 "synthesis": "Hi, I'm Agent MSA. I'm here to help you with Microservices Architecture.",
                 "sources": []
             }

        # 1. Strict Domain Guardrail
        if not self.validate_intent(user_query):
             print(f"DEBUG: Query blocked by guardrails: '{user_query}'")
             return "I am strictly bound to answer only questions about Microservices Architecture. \n\nPlease include relevant terms (e.g., 'API', 'Docker', 'Service', 'Scaling') in your question."
        
        all_candidates = []
        
        # 1. Search Knowledge Base First (Offline/Indexed Layer)
        kb_results = self.search_knowledge_base(user_query)
        if kb_results:
            print(f"DEBUG: Using {len(kb_results)} results from Knowledge Base.")
            all_candidates.extend(kb_results)
            
        # 2. Search Live API (Online Layer)
        # Always search live to "Index on Read" and get fresh data
        raw_items = self.search_questions(user_query)
        live_candidates = self.fetch_answers(raw_items)
        
        # Index verified answers for future
        for cand in live_candidates:
            if cand['is_accepted']:
                self.index_knowledge(cand)
                
        all_candidates.extend(live_candidates)
        
        if not all_candidates:
             return "I am bound to answer only questions about microservices. Please ask a relevant question."
        
        # 3. Rank & Verify
        ranked = self.rank_candidates(user_query, all_candidates)
        
        # 4. Generate Synthesis
        summary = self.generate_verified_answer(user_query, ranked)

        # Format for frontend
        results = []
        for r in ranked:
            results.append({
                "title": html.unescape(r["title"]),
                "answer": r["answer_text"][:500] + "...", 
                "summary": r["answer_text"][:200] + "...", 
                "link": r["link"],
                "score": r["hybrid_score"] * 100, # Scale to 0-100 for UI
                "date": datetime.fromtimestamp(r["creation_date"]).strftime('%Y-%m-%d'),
                "votes": r["score"],
                "accepted": r["is_accepted"],
                "reputation": r["reputation"],
                "source_type": r.get("source_type", "Live API")
            })

        return {
            "synthesis": summary,
            "sources": results
        }

if __name__ == "__main__":
    # Load env for local testing
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("DEBUG: Environment loaded.")
    except ImportError:
        print("DEBUG: dotenv not found.")

    agent = AgentMSA()
    q = input("Query: ")
    res = agent.ask(q)
    print(res["synthesis"])
