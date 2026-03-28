FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency manifest first to maximize Docker layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

# The MCP CLI discovers the FastMCP instance from main.py and serves it.
CMD ["python", "main.py"]

