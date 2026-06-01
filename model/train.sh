#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="$SCRIPT_DIR"
API_DIR="$PROJECT_ROOT/api"
MODEL_FILE="waldo_model.pth"
IMAGE_NAME="waldo-model-trainer"

echo "============================================"
echo "  Waldo - Treinamento do Modelo"
echo "============================================"


echo ""
echo "[1/3] Construindo imagem Docker do treinamento..."
docker build -t "$IMAGE_NAME" "$MODEL_DIR"

GPU_FLAG=""
if docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
  echo "      GPU NVIDIA detectada — treinamento com GPU ativado."
  GPU_FLAG="--gpus all"
else
  echo "      GPU não detectada — treinamento via CPU (pode ser lento)."
fi

echo ""
echo "[2/3] Iniciando treinamento..."
docker run --rm \
  $GPU_FLAG \
  -v "$MODEL_DIR":/app \
  "$IMAGE_NAME" train.py

if [ ! -f "$MODEL_DIR/$MODEL_FILE" ]; then
  echo ""
  echo "ERRO: O arquivo '$MODEL_FILE' não foi gerado em $MODEL_DIR"
  echo "Verifique os logs do treinamento acima."
  exit 1
fi

# Copia o modelo treinado pra pasta da API
echo ""
echo "[3/3] Copiando '$MODEL_FILE' para a API ($API_DIR)..."
cp "$MODEL_DIR/$MODEL_FILE" "$API_DIR/$MODEL_FILE"

echo ""
echo "============================================"
echo "  Treinamento concluído com sucesso!"
echo "  Modelo disponível em: $API_DIR/$MODEL_FILE"
echo "============================================"
echo ""
echo "Para aplicar o novo modelo, reinicie o backend:"
echo "  docker compose up --build -d"
