from microservices_agent_v2 import AgentMSA
import time

print("Initializing Agent...")
start = time.time()
agent = AgentMSA()
print(f"Agent initialized in {time.time() - start:.2f}s")

query = "What is the difference between SOA and microservices?"
print(f"Asking: {query}")
start = time.time()
res = agent.ask(query)
print(f"Response received in {time.time() - start:.2f}s")
if isinstance(res, dict):
    print("Synthesis:", res["synthesis"][:100], "...")
    print("Sources:", len(res["sources"]))
else:
    print("Result:", res)
