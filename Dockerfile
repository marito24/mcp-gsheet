FROM python:3.12-slim

# --- 1. Dependencias básicas ---
RUN apt-get update -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Evita archivos .pyc y cache innecesaria
ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# --- 2. Herramientas y SDK MCP ---
# uv  → gestor de dependencias recomendado
# mcp → CLI oficial para arrancar servidores
RUN pip install --no-cache-dir uv mcp \
    google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib

# --- 3. Clonar tu fork ---
RUN git clone https://github.com/TU-USUARIO/mcp-gsheet /app/mcp-gsheet
WORKDIR /app/mcp-gsheet

# --- 4. Instalar las deps del proyecto con uv ---
RUN uv pip install -e .

# --- 5. Variables de entorno (Railway inyectará $PORT) ---
ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

# --- 6. Arranque del servidor en modo HTTP streamable ---
CMD ["mcp", "run", "server.py",
     "--transport", "streamable-http",
     "--host", "0.0.0.0",
     "--port", "${PORT}"]
