FROM python:3.12-slim

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir uv

# 3 ) Clona repo público
RUN git clone https://github.com/shionhonda/mcp-gsheet.git /opt/mcp-gsheet
WORKDIR /opt/mcp-gsheet

# 4 ) Instala dependencias del proyecto
RUN uv pip install -e .

ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

CMD ["uvx","mcp-gsheet","--transport","streamable-http","--host","0.0.0.0","--port","${PORT}"]
