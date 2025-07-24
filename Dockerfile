FROM python:3.12-slim

# 1) Dependencias básicas
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# 2) Instala uv (gestor de dependencias ultra‑rápido)
RUN pip install --no-cache-dir uv

# 3) Clona el repo público con el servidor MCP
RUN git clone https://github.com/shionhonda/mcp-gsheet.git /opt/mcp-gsheet
WORKDIR /opt/mcp-gsheet

# 4) Instala el propio proyecto y las librerías de Google **dentro del sistema**
RUN uv pip install --system -e . \
    google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib

# 5) Variables que necesita el servidor y que Railway completará
ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

# 6) Arranque: servidor MCP en modo HTTP
CMD ["uvx","mcp-gsheet","--transport","streamable-http","--host","0.0.0.0","--port","${PORT}"]
