FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y build-essential curl software-properties-common

RUN curl -fsSL https://ollama.com/install.sh | sh && \
    ollama serve & \
    sleep 10 && \
    ollama pull phi3

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 8000

CMD ["sh", "-c", "ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]