import json
import os
from typing import List, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

INDEX_PATH = os.getenv("INDEX_PATH", "./index.faiss")
META_PATH = os.getenv("META_PATH", "./metadata.json")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://ollama:11434")
K_DEFAULT = 5

def load_metadata(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_vectorstore(index_path: str):
    embedder = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_EMBED_URL)
    return FAISS.load_local(index_path, embedder, allow_dangerous_deserialization=True)


print("Carregando vetorstore FAISS...")
vectorstore = load_vectorstore(INDEX_PATH)

print("Carregando metadados...")
metadata = load_metadata(META_PATH)

print("Sistema de busca pronto.")

app = FastAPI(title="Semantic Retriever Service")


class QueryRequest(BaseModel):
    query: str
    k: int = K_DEFAULT


@app.post("/search")
def semantic_search(payload: QueryRequest):
    query = payload.query
    k = payload.k

    print(f"Recebida query: '{query}', buscando top-{k}...")

    results = vectorstore.similarity_search_with_score(query, k=k)

    response = []
    for doc, score in results:
        entry = {
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        }
        response.append(entry)

    return {
        "query": query,
        "k": k,
        "results": response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)