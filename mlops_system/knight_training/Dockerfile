FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends rsync openssh-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/
COPY config/ config/

EXPOSE 8082

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8082"]
