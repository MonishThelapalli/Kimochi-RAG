FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1
ENV CUDA_VISIBLE_DEVICES=""
ENV TORCH_CUDA_ARCH_LIST=""

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.1.2+cpu \
    torchvision==0.16.2+cpu \
    torchaudio==2.1.2+cpu \
    -f https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
