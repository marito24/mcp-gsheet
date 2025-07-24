FROM python:3.12-slim

# 1) Utilidades mínimas
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    # 👉 Desactiva el layout‑discovery de setuptools
    SETUPTOOLS_ENABLE_LAYOUT_DISCOVERY=0

# 2) Clona el repo original (o tu fork público)
RUN git clone https://github.com/shionhonda/mcp-gsheet.git /opt/mcp-gsheet
WORKDIR /opt/mcp-gsheet

# 3) Fija setuptools a una versión estable y
#    instala el proyecto + libs de Google
RUN pip install --no-cache-dir --upgrade pip 'setuptools<69' wheel && \
    pip install --no-cache-dir -e . \
        google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib

# 4) Variables que Railway ya conoce
ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

# 5) Arranque: servidor MCP vía uvx
RUN pip install --no-cache-dir uv
CMD ["uvx","mcp-gsheet","--transport","streamable-http","--host","0.0.0.0","--port","${PORT}"]
