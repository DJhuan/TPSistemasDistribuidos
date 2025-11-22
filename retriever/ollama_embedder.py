import requests
from typing import List

class SimpleOllamaEmbeddings:
    def __init__(self, model="nomic-embed-text", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def embed_query(self, text: str) -> List[float]:
        payload = {
            "model": self.model,
            "prompt": text
        }
        r = requests.post(f"{self.base_url}/api/embeddings", json=payload)
        r.raise_for_status()
        return r.json()["embedding"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]