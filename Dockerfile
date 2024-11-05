FROM python:3.12-slim AS builder

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

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8055

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8055", "run:app"]
