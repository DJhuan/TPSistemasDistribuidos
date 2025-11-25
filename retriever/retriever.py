import json
import os
import time
from typing import List, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Configurações
INDEX_PATH = os.getenv("INDEX_PATH", "/app/index.faiss")
META_PATH = os.getenv("META_PATH", "/app/metadata.json")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://ollama:11434")
K_DEFAULT = 5

app = FastAPI(title="Semantic Retriever Service")

# Variável global para armazenar o banco carregado
vectorstore = None

def load_metadata(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def aguardar_indice():
    """Espera o indexer criar os arquivos antes de tentar carregar."""
    global vectorstore
    
    # O FAISS salva como uma pasta. Precisamos verificar se o arquivo dentro dela existe.
    # Geralmente é index.faiss dentro da pasta definida no path.
    caminho_arquivo_real = os.path.join(INDEX_PATH, "index.faiss")
    
    print(f"Verificando existência do índice em: {INDEX_PATH}...")
    
    # Loop infinito até o arquivo aparecer
    while not os.path.exists(INDEX_PATH) or not os.path.exists(caminho_arquivo_real):
        print("Índice ainda não existe. O Indexer ainda está processando o PDF... (Aguardando 10s)")
        time.sleep(10)
    
    print("Índice encontrado! Carregando FAISS...")
    try:
        embedder = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_EMBED_URL)
        vectorstore = FAISS.load_local(INDEX_PATH, embedder, allow_dangerous_deserialization=True)
        print("✅ Vetorstore carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar índice (tentaremos novamente): {e}")

@app.on_event("startup")
async def startup_check():
    """Roda automaticamente quando o servidor inicia"""
    # Em produção ideal, isso seria assíncrono ou um health check, 
    # mas para este projeto, bloquear a inicialização até ter dados é o mais seguro.
    aguardar_indice()

class QueryRequest(BaseModel):
    query: str
    k: int = K_DEFAULT

@app.post("/search")
def semantic_search(payload: QueryRequest):
    if vectorstore is None:
        raise HTTPException(status_code=503, detail="O índice ainda está sendo criado. Tente novamente em alguns segundos.")

    query = payload.query
    k = payload.k

    print(f"Recebida query: '{query}', buscando top-{k}...")
    
    try:
        results = vectorstore.similarity_search_with_score(query, k=k)

        response = []
        for doc, score in results:
            entry = {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            response.append(entry)

            # Imprime os dados da resposta do RAG
            print("--- Resultado ---")
            print(f"Texto: {doc.page_content}")
            print(f"Metadados: {doc.metadata}")
            print(f"Score: {score}")

        return {
            "query": query,
            "k": k,
            "results": response
        }
    except Exception as e:
        print(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)