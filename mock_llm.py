# mock_llm.py
# (Um servidor "falso" para simular o serviço do Jhuan)

from fastapi import FastAPI, Request
from pydantic import BaseModel
import time

app = FastAPI(title="Mock LLM Service")

#1. define os modelos de dados que a api espera
class LLMRequest(BaseModel):
    prompt_usuario: str
    contexto_rag: list[str]

class LLMResponse(BaseModel):
    analise: str
    acoes_sugeridas: str

#2. implementa o endpoint /generate na porta 8002
@app.post("/generate", response_model=LLMResponse)
async def generate_response(request_data: LLMRequest, request: Request):
    """
    Simula a API do Jhuan.
    Ele recebe a requisição, imprime no console e devolve uma resposta "fake".
    """
    
    #imprime no terminal para ver que foi chamado
    print("\n--- Mock LLM Recebeu uma Chamada! ---")
    print(f"IP de quem chamou: {request.client.host}")
    print(f"Prompt do Usuário: {request_data.prompt_usuario[:50]}...")
    print(f"Documentos do RAG recebidos: {len(request_data.contexto_rag)}")
    print("--------------------------------------\n")
    
    # Simula um "delay" (o LLM pensando)
    time.sleep(1) 

    # 3. Devolve a resposta "fake" (o contrato)
    return LLMResponse(
        analise="ISSO É UMA RESPOSTA DE TESTE: A ação de faltar sem aviso prévio é considerada uma violação do Artigo 5 do estatuto de conduta.",
        acoes_sugeridas="ISSO É UMA SUGESTÃO DE TESTE: 1. Conversar com o membro. 2. Aplicar advertência formal."
    )

@app.get("/health")
def health_check():
    return {"status": "Mock LLM está operacional"}

# Para rodar: uvicorn mock_llm:app --port 8002