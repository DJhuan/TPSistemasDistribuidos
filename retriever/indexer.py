import pdfplumber
import json
import requests
import os
import faiss
from uuid import uuid4
import numpy as np

OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11434/api/embed")
CHUNK_SIZE = 1000   #tamanho de cada chunk
CHUNK_OVERLAP = 200 #intersecção entre cada chunk
PDF_DIR = "./pdfs"
INDEX_PATH = "./index.faiss"
META_PATH = "./metadata.json"
EMBED_MODEL = "nomic-embed-text"

def extract_text_from_pdf(path):
    texts = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            txt = p.extract_text()
            if txt:
                texts.append(txt)
    return "\n".join(texts)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    i = 0
    L = len(text)
    while i < L:
        end = min(i + size, L)
        chunk = text[i:end]
        chunks.append(chunk.strip())
        i += size - overlap
    return chunks

def embed_texts(texts, model=EMBED_MODEL):
    # Use the Ollama HTTP embed endpoint to get embeddings for a batch of texts.
    # `texts` can be a single string or a list of strings.
    payload = { "model": model, "input": texts }
    try:
        resp = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if "embeddings" not in data:
            raise ValueError(f"unexpected embed response: {data}")
        return data["embeddings"]
    except Exception as e:
        print("Failed to get embeddings from Ollama:", e)
        raise

def main():
    metas = []
    all_embeddings = []

    for filename in os.listdir(PDF_DIR):
        if not filename.lower().endswith(".pdf"):
            continue
        path = os.path.join(PDF_DIR, filename)
        print("Processing", filename)
        text = extract_text_from_pdf(path)
        chunks = chunk_text(text)
        texts_for_embed = []
        
        for id, chunk in enumerate(chunks):
            chunk_id = str(uuid4()) #cria um id unico
            metas.append({
                "chunk_id": chunk_id,
                "doc": filename,
                "chunk_index": id,
                "text": chunk[:1000]
            })
            texts_for_embed.append(chunk)

        BATCH = 32
        for i in range(0, len(texts_for_embed), BATCH):
            batch = texts_for_embed[i: i+BATCH]
            embeddings = embed_texts(batch)
            all_embeddings.extend(embeddings)

    X = np.array(all_embeddings).astype('float32')
    dim = X.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(X)
    faiss.write_index(index, INDEX_PATH)
    
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)
    print("index built:", INDEX_PATH, "meta:", META_PATH)

if __name__ == "__main__":
    main()