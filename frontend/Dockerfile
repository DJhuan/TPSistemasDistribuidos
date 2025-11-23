# Imagem base
FROM python:3.10-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Instalação das dependências
COPY requirements.txt .

# Roda o pip install. O Docker "guarda" essa camada.
RUN pip install --no-cache-dir -r requirements.txt

# Cópia do código
COPY . .

# Porta de exposição
EXPOSE 8501

# Comando para rodar
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]