FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/
COPY config/ config/

EXPOSE 8083

CMD ["uvicorn", "src.dashboard_api:app", "--host", "0.0.0.0", "--port", "8083"]
