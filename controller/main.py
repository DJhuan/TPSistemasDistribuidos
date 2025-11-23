import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import os

# Configuração básica de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Controller")

app = FastAPI(title="Têmis Business Controller")

# Definição de URLs dos microsserviços
# O padrão assume que os serviços estão rodando na mesma rede Docker com seus nomes de serviço
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://retriever:5000/search")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8024/judge")

class CondutaRequest(BaseModel):
    descricao: str

@app.post("/orquestrar_analise")
async def orquestrar(data: CondutaRequest):
    """
    Recebe a descrição do Gateway, busca normas no RAG, 
    manda pro LLM e devolve a resposta.
    """
    logger.info("Controller: Iniciando orquestração da conduta.")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # --- PASSO 1: BUSCAR NO RAG ---
        contexto_final = []
        try:
            logger.info(f"Buscando no RAG: {RAG_SERVICE_URL}")
            # O Retriever espera "query" e "k"
            rag_resp = await client.post(RAG_SERVICE_URL, json={"query": data.descricao, "k": 3})
            rag_resp.raise_for_status()
            
            # Extração dos resultados
            dados_rag = rag_resp.json()
            lista_resultados = dados_rag.get("results", [])
            
            # Extrai apenas o texto dos documentos encontrados
            contexto_final = [item.get("text", "") for item in lista_resultados if item.get("text")]
            
            if not contexto_final:
                logger.warning("RAG retornou lista vazia. Usando conhecimento geral.")
                contexto_final = ["Nenhuma norma específica encontrada no banco de dados."]

        except Exception as e:
            logger.error(f"Erro ao consultar RAG: {e}")
            # Não paramos o sistema se o RAG falhar, tentamos seguir só com o LLM
            contexto_final = ["Erro de conexão com o banco de normas."]

        # --- PASSO 2: ENVIAR PARA O LLM ---
        try:
            logger.info(f"Enviando para LLM: {LLM_SERVICE_URL}")
            llm_payload = {
                "prompt_usuario": data.descricao,
                "contexto_rag": contexto_final
            }
            
            llm_resp = await client.post(LLM_SERVICE_URL, json=llm_payload)
            llm_resp.raise_for_status()
            
            resultado = llm_resp.json()
            
        except Exception as e:
            logger.error(f"Erro crítico no LLM: {e}")
            raise HTTPException(status_code=502, detail="O módulo de Inteligência Artificial falhou.")

    logger.info("Controller: Orquestração finalizada com sucesso.")
    return resultado