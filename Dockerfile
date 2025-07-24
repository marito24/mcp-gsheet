# ---- Imagen base ----
FROM python:3.12-slim

# Dependencias mínimas
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Librerías que usa el servidor
RUN pip install --no-cache-dir \
        fastapi uvicorn[standard] \
        google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib

# Clonamos el servidor (repo público)
RUN git clone https://github.com/shionhonda/mcp-gsheet.git /opt/mcp-gsheet
WORKDIR /opt/mcp-gsheet

# ----- VARS que Railway inyectará -----
ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

# ---- Arranque: ejecutamos el server.py tal cual ----
CMD ["python", "server.py", "--transport", "streamable-http",
     "--host", "0.0.0.0", "--port", "${PORT}"]
