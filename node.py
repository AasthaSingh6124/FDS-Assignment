from flask import Flask, request, jsonify
import threading
import requests
import time
import json
import os

app = Flask(__name__)

NODE_ID = os.environ["NODE_ID"]
ALL_NODES = json.loads(os.environ["ALL_NODES"])
NODES = list(ALL_NODES.keys())

vector_clock = {nid: 0 for nid in NODES}
kv_store = {}
buffer = []

lock = threading.Lock()

@app.route('/get/<key>', methods=['GET'])
def get_key(key):
    return jsonify({"value": kv_store.get(key, None), "vc": vector_clock})

@app.route('/put/<key>', methods=['PUT'])
def put_key(key):
    data = request.json
    value = data["value"]

    with lock:
        vector_clock[NODE_ID] += 1
        kv_store[key] = value

        payload = {
            "sender": NODE_ID,
            "key": key,
            "value": value,
            "vc": vector_clock.copy()
        }

    for nid, url in ALL_NODES.items():
        if nid != NODE_ID:
            try:
                requests.post(f"{url}/replicate", json=payload)
            except:
                pass

    return jsonify({"status": "ok", "vc": vector_clock})

@app.route('/replicate', methods=['POST'])
def replicate():
    data = request.json
    with lock:
        buffer.append(data)
    return jsonify({"status": "buffered"})

def check_causal_delivery():
    while True:
        with lock:
            delivered = []
            for msg in buffer:
                sender = msg["sender"]
                vc = msg["vc"]
                if all(vc[n] <= vector_clock[n] for n in NODES if n != sender) and vc[sender] == vector_clock[sender] + 1:
                    kv_store[msg["key"]] = msg["value"]
                    vector_clock[sender] += 1
                    delivered.append(msg)
            for msg in delivered:
                buffer.remove(msg)
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=check_causal_delivery, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)

