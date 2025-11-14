import os
import json
from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

PDF_DIR = "./pdfs"
INDEX_PATH = "./index.faiss"
META_PATH = "./metadata.json"
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://ollama:11434")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBED_MODEL = "nomic-embed-text"

def load_pdfs(pdf_dir: str) -> List[Dict]:
    """Carrega todos os PDFs de um diretório e retorna uma lista de documentos."""
    docs = []
    pdf_dir = Path(pdf_dir)

    for pdf_file in pdf_dir.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        pdf_docs = loader.load()

        for d in pdf_docs:
            d.metadata["source"] = pdf_file.name
        
        docs.extend(pdf_docs)

    return docs

def chunk_documents(docs: List[Dict]) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_documents(docs)
    return chunks

def get_embedder():
    return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_EMBED_URL)


def build_faiss_index(chunks: List[Dict]):
    embedder = get_embedder()

    print("[1/2] Gerando embeddings...")
    vectorstore = FAISS.from_documents(chunks, embedder)

    print("[2/2] Salvando índice FAISS...")
    vectorstore.save_local(INDEX_PATH)

    return vectorstore

def save_metadata(chunks: List[Dict]):
    metadata_list = [
        {
            "text": c.page_content,
            "source": c.metadata.get("source", "unknown"),
            "page": c.metadata.get("page", None)
        }
        for c in chunks
    ]

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=4, ensure_ascii=False)

def main():
    print("Carregando PDFs...")
    docs = load_pdfs(PDF_DIR)

    print(f"{len(docs)} páginas encontradas.")

    print("Gerando chunks...")
    chunks = chunk_documents(docs)
    print(f"{len(chunks)} chunks gerados.")

    print("Construindo índice vetorial FAISS...")
    build_faiss_index(chunks)

    print("Salvando metadados...")
    save_metadata(chunks)

    print("Indexação concluída com sucesso!")


if __name__ == "__main__":
    main()