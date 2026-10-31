FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY server/requirements.txt /work/server/requirements.txt
RUN python3 -m venv /opt/savia-venv \
    && /opt/savia-venv/bin/pip install --no-cache-dir -r /work/server/requirements.txt
COPY server/ /work/server/

ENV PATH=/opt/savia-venv/bin:$PATH \
    SAVIA_DB_KIND=sqlite \
    SAVIA_DATA_DIR=/data \
    SAVIA_HOST=0.0.0.0 \
    SAVIA_PORT=8000
EXPOSE 8000
CMD ["python3", "server/app.py"]
