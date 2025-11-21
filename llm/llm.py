import uvicorn
import os
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

MODEL_NAME = os.getenv("LLM_MODEL", "google-gla:gemini-2.5-flash")
PROMPT = "Um pato e uma vaca foram competir, quem correu mais rápido até a chegada?"

# Definição REQ <-> RES;
class LLMRequest(BaseModel):
    """Modelo de requisição para o microsserviço LLM."""
    prompt_usuario: str
    contexto_rag: list[str]

class LLMResponse(BaseModel):
    """Modelo de resposta do microsserviço LLM."""
    analise: str = Field(description="A análise jurídica detalhada da conduta.")
    acoes_sugeridas: str = Field(description="Lista de ações recomendadas baseadas na análise.")

# Agente usado para interagir com o modelo LLM;
the_judge = Agent(
    MODEL_NAME,
    output_type=LLMResponse,
    system_prompt="""
        Você é um assistente jurídico especializado em Compliance.
        Seu objetivo é analisar condutas com base na descrição da situação,
        fornecida pelo time da empresa, e no contexto adicional fornecido pelo
        sistema de Recuperação de Informação (RAG) alimentado com a
        documentação da empresa.
        A análise da conduta deve considerar as políticas internas da empresa,
        e, além da análise, você deve sugerir ações concretas que a empresa
        pode tomar para lidar com a situação descrita.
        Utilize o contexto fornecido para fundamentar sua análise e
        recomendações.
        Seja claro, objetivo e detalhado em suas respostas.
        """
)

# Definição da API do microsserviço LLM;

app = FastAPI(title="Microsserviço LLM para Análise Jurídica", version="1.0.0")

@app.post("/judge", response_model=LLMResponse)
async def generate_analysis(request: LLMRequest):
    """Recebe a descrição e o contexto do RAG, processa via LLM e retorna JSON estruturado."""
    try:
        contexto_str = "\n---\n".join(request.contexto_rag)
        
        prompt_final = (
            f"DESCRIÇÃO DA CONDUTA:\n{request.prompt_usuario}\n\n"
            f"CONTEXTO JURÍDICO/REGULATÓRIO (RAG):\n{contexto_str}\n\n"
            "Instrução: Analise a conduta junto do contexto fornecido."
        )

        result = await the_judge.run(prompt_final)
        
        print(result)
        return result.output

    except Exception as e:
        print(f"Erro no processamento LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "Juíz rodando! Tudo OK."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8024)