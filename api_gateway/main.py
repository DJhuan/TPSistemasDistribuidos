import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Têmis API Gateway")

#URLs dos microserviços lidas do .env
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:5000/search")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8002/generate")

class CondutaRequest(BaseModel):
    descricao: str

class AnaliseResponse(BaseModel):
    analise_completa: str
    acoes_sugeridas: str

async def get_current_user(request: Request):
    """
    (Placeholder de Autenticação)
    Valida se o usuário tem um token de autorização.
    No futuro, pode ser trocado por uma validação JWT.
    """
    token = request.headers.get("Authorization")
    if not token:
        logger.warning("Acesso sem token de autorização.")
        #em produção:
        #raise HTTPException(status_code=401, detail="Token de autorização ausente")
    
    #simula um usuario valido
    user = {"username": "usuario_teste_comp"} 
    logger.info(f"Usuário autenticado: {user['username']}")
    return user


@app.post("/analisar_conduta", response_model=AnaliseResponse)
async def analisar_conduta(
    request_data: CondutaRequest, 
    user: dict = Depends(get_current_user)
):
    """
    Endpoint principal: Orquestra a análise de conduta.
    """
    logger.info(f"Iniciando análise para o usuário: {user['username']}")

    try:
        #1. chamar o serviço RAG para buscar documentos
        async with httpx.AsyncClient() as client:
            logger.info(f"Consultando RAG: {request_data.descricao[:50]}...")
            rag_payload = {"query": request_data.descricao}
            
            rag_response = await client.post(
                RAG_SERVICE_URL, 
                json=rag_payload,
                timeout=10.0
            )
            rag_response.raise_for_status() #lança exceçao se o RAG falhar
            
            #extrai os textos ("snippets") da resposta do RAG
            chunks = rag_response.json().get("chunks", [])
            documentos_relevantes = [
                chunk.get("snippet", "") 
                for chunk in chunks 
                if chunk.get("snippet")
            ]
            
            if not documentos_relevantes:
                logger.warning("RAG não retornou documentos relevantes.")

            #2. chamar o serviço LLM com o prompt e o contexto
            logger.info("Enviando dados para o LLM...")
            
            llm_payload = {
                "prompt_usuario": request_data.descricao,
                "contexto_rag": documentos_relevantes
            }
            
            llm_response = await client.post(
                LLM_SERVICE_URL,
                json=llm_payload,
                timeout=30.0
            )
            llm_response.raise_for_status() #lança exceçao se o LLM falhar

            #3. retornar a resposta final do LLM
            resposta_final_json = llm_response.json()
            logger.info("Análise concluída com sucesso.")

            return AnaliseResponse(
                analise_completa=resposta_final_json.get("analise", "Resposta de análise não encontrada."),
                acoes_sugeridas=resposta_final_json.get("acoes_sugeridas", "Nenhuma ação sugerida.")
            )

    except httpx.HTTPStatusError as e:
        #erro de um dos outros serviços (ex: 404, 500)
        logger.error(f"Erro no microserviço ({e.request.url}): {e.response.status_code}")
        raise HTTPException(status_code=502, detail=f"Erro de comunicação com microserviço: {e.response.text}")
    except httpx.RequestError as e:
        #erro de conexão (ex: serviço offline)
        logger.error(f"Não foi possível conectar ao serviço {e.request.url}: {e}")
        raise HTTPException(status_code=503, detail=f"Serviço indisponível: {e.request.url}")
    except Exception as e:
        logger.error(f"Erro inesperado no gateway: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")

@app.get("/health")
def health_check():
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "API Gateway está operacional"}