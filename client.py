import requests
import time

NODES = {
    "node1": "http://localhost:8001",
    "node2": "http://localhost:8002",
    "node3": "http://localhost:8003"
}

# Write to node1
res = requests.put(f"{NODES['node1']}/put/x", json={"value": "A"})
print("PUT x=A to node1:", res.json())

time.sleep(2)

# Write to node2
res = requests.put(f"{NODES['node2']}/put/x", json={"value": "B"})
print("PUT x=B to node2:", res.json())

time.sleep(2)

# Read from node3
res = requests.get(f"{NODES['node3']}/get/x")
print("GET x from node3:", res.json())

