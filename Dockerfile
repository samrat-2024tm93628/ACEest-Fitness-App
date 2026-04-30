# syntax=docker/dockerfile:1.7

# ---- Stage 1: build deps into an isolated prefix ----
FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---- Stage 2: minimal runtime image ----
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DB_PATH=/data/aceest.db \
    PORT=5000

RUN useradd --create-home --uid 1001 ace \
    && mkdir -p /data \
    && chown -R ace:ace /data

WORKDIR /app

COPY --from=build /install /usr/local
COPY --chown=ace:ace app.py ./

USER ace

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:5000/health').status==200 else sys.exit(1)" || exit 1

CMD ["python", "app.py"]
