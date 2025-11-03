FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    tesseract-ocr \
    tesseract-ocr-rus \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY entrypoint.sh .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install alembic

COPY alembic/ alembic/
COPY alembic.ini .
COPY app/ app/

RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/app

RUN mkdir -p /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2
COPY ./onnx_model/ /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/

RUN cd /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/ && \
    tar -czf onnx.tar.gz config.json model.onnx special_tokens_map.json tokenizer.json tokenizer_config.json vocab.txt

ENV CHROMA_SERVER_NOFILE=1
ENV CHROMA_DISABLE_TELEMETRY=1
ENV CHROMA_DISABLE_IMPORT=1

CMD ["bash", "/app/entrypoint.sh"]
