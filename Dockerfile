FROM python:3.12-slim

# Instala dependências de sistema necessárias para o psycopg2 e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o container
COPY . .

# Expõe a porta do FastAPI
EXPOSE 8000

# Define o PYTHONPATH para resolver a importação do módulo src
ENV PYTHONPATH=/app

# Comando padrão para rodar a aplicação em modo de desenvolvimento
CMD ["uvicorn", "src.infrastructure.web.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
