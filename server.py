from flask import Flask, request, jsonify
from flask_cors import CORS
from microservices_agent_v2 import AgentMSA
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Agent
agent = AgentMSA()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "AgentMSA Backend is Online (Lite Mode)"})

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        results = agent.ask(query)
        if isinstance(results, str):
             return jsonify({"results": [], "message": results})
        
        # New format returns dict with 'synthesis' and 'sources'
        if isinstance(results, dict) and "synthesis" in results:
            return jsonify({
                "results": results["sources"], 
                "synthesis": results["synthesis"]
            })
            
        # Fallback: if results is valid data (e.g. list) but no synthesis
        return jsonify({
            "results": results,
            "synthesis": "Here are the relevant search results."
        })
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
