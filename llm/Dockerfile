FROM python:3.10-slim

WORKDIR /app

# Dizem as más linguas que ajuda a otimizar o python no docker;
# Evita __pyccache__;
ENV PYTHONDONTWRITEBYTECODE=1
# Desabilita buffer para escritas;
ENV PYTHONUNBUFFERED=1

# Instalação de dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY main.py .

# Expõe a porta 8024
EXPOSE 8024

ENV LLM_MODEL="google-gla:gemini-2.5-flash"

# Comando de execução
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8024"]