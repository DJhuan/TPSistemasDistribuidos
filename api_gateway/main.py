import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Gateway")

app = FastAPI(title="Têmis API Gateway (Entry Point)")

# O Gateway fala com o Controller.
# Nome do serviço no Docker: controller-service
# Porta do Controller: Vamos definir como 8001 para não confundir
CONTROLLER_URL = os.getenv("CONTROLLER_URL", "http://controller-service:8001/orquestrar_analise")

class CondutaRequest(BaseModel):
    descricao: str

@app.get("/health")
def health():
    return {"status": "Gateway Online"}

@app.post("/analisar_conduta")
async def proxy_analise(request: CondutaRequest):
    """
    Função do Gateway:
    1. Receber do Front
    2. (Opcional) Validar Token/Auth aqui
    3. Repassar para o Controller de Negócio
    """
    logger.info("Gateway: Recebendo requisição. Repassando ao Controller...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Repassa exatamente o que recebeu para o Controller
            resp = await client.post(CONTROLLER_URL, json=request.model_dump())
            
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            
            return resp.json()

    except httpx.RequestError as e:
        logger.error(f"Gateway falhou ao conectar no Controller: {e}")
        raise HTTPException(status_code=503, detail="Serviço de Orquestração indisponível.")