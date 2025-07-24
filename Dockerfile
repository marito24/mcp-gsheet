FROM python:3.12-slim

# Evita archivos innecesarios
ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instala dependencias básicas
RUN apt-get update && apt-get install -y git && \
    pip install --no-cache-dir uv

# Clona tu fork de mcp-gsheet (REEMPLAZA por tu propio repo si quieres)
RUN git clone https://github.com/shionhonda/mcp-gsheet.git /app/mcp-gsheet

# Entra en la carpeta y lo instala como paquete local
WORKDIR /app/mcp-gsheet
RUN pip install .

# Define variables
ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

# Copia la clave si quieres subirla tú (si no, la montas con Railway Secrets)
# COPY sa.json /app/sa.json

EXPOSE ${PORT}

# Arranca el servidor MCP
CMD ["uvx", "mcp-gsheet", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "${PORT}"]

