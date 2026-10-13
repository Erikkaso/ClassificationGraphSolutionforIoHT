FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY Requirements.txt ./Requirements.txt
RUN pip install --no-cache-dir -r Requirements.txt \
    && pip install --no-cache-dir gunicorn supervisor

COPY API ./API
COPY Server ./Server
COPY download ./download
COPY docker ./docker

RUN groupadd --system graph \
    && useradd --system --gid graph --home-dir /app --shell /usr/sbin/nologin graph \
    && chown -R graph:graph /app

USER graph

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/', timeout=3)"

CMD ["/usr/local/bin/supervisord", "-c", "/app/docker/supervisord.conf", "-n"]
