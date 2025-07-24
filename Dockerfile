FROM python:3.12-slim

# 1 ) dependencias básicas
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 2 ) gestor ‘uv’
RUN pip install --no-cache-dir uv

# 3 ) clona TU fork  ➜  **cambia mario‑username por tu usuario**
RUN git clone https://github.com/mario-username/mcp-gsheet /opt/mcp-gsheet
WORKDIR /opt/mcp-gsheet

# 4 ) instala el paquete y sus dependencias
RUN uv pip install -e .

# 5 ) variables que Railway inyectará
ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

# 6 ) ARRANQUE  ➜  todo en UNA línea JSON
CMD ["uvx","mcp-gsheet","--transport","streamable-http","--host","0.0.0.0","--port","${PORT}"]
