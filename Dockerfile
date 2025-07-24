FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir uv mcp-gsheet

ENV SERVICE_ACCOUNT_PATH=/app/sa.json \
    PORT=${PORT:-8000}

EXPOSE ${PORT}

CMD ["uvx", "mcp-gsheet", "--tra]()
