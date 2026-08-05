FROM python:3.12-slim AS builder

ARG BUILD_VERSION=2.0.0
ARG BUILD_SHA=unknown
ARG BUILD_DATE=unknown

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_linux.txt && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim

ARG BUILD_VERSION=2.0.0
ARG BUILD_SHA=unknown
ARG BUILD_DATE=unknown

ENV BUILD_VERSION=${BUILD_VERSION} \
    BUILD_SHA=${BUILD_SHA} \
    BUILD_DATE=${BUILD_DATE}

LABEL org.opencontainers.image.title="ChoreBoss" \
      org.opencontainers.image.version="$BUILD_VERSION" \
      org.opencontainers.image.revision="$BUILD_SHA" \
      org.opencontainers.image.created="$BUILD_DATE"

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8055

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8055"]
