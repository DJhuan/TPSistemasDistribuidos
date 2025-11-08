from flask import Flask, request, jsonify
import faiss
import numpy as np
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
INDEX_PATH = os.getenv("INDEX_PATH", "./index.faiss")
META_PATH = os.getenv("META_PATH", "./metadata.json")
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11434/api/embed")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metas = json.load(f)

app = Flask(__name__)

def embed_query(q):
    resp = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL, "input": q}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    emb = data["embeddings"][0]
    return np.array(emb).astype('float32')

@app.route("/search", methods=["POST"])
def search():
    body = request.get_json() or {}
    q = body.get("query", "")
    k = int(body.get("k", 5))
    if not q:
        return jsonify({"error":"empty_query"}), 400
    q_emb = embed_query(q)
    D, I = index.search(np.array([q_emb]), k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        meta = metas[idx]
        results.append({
            "chunk_id": meta["chunk_id"],
            "doc": meta["doc"],
            "score": float(score),
            "snippet": meta["text"]
        })
    return jsonify({"chunks": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)