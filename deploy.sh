#!/bin/bash
# MODE を "local" か "gcp" で指定
MODE=${1:-local}

# 共通パラメータ
IMAGE_NAME="dhs_corr"
TAG="ver1.01"

if [ "$MODE" = "local" ]; then
  echo "===== ローカル実行モード ====="

  # Docker build (Apple Silicon/Mac用)
  docker build --platform=linux/arm64 -t ${IMAGE_NAME}:${TAG} .

  # ローカルでコンテナRun
  docker run -it --rm -p 8080:8080 ${IMAGE_NAME}:${TAG}

elif [ "$MODE" = "gcp" ]; then
  echo "===== GCPデプロイモード ====="
  
  # GCP用パラメータ
  PROJECT_ID="snakada-personal"
  REPOSITORY="docker-nakada"
  REGION="us-west1"
  SERVICE_NAME="dhs-stunting"

  # Docker build (Apple Silicon対応)
  docker build --platform=linux/amd64 -t ${IMAGE_NAME}:${TAG} .

  # タグ付け
  docker tag ${IMAGE_NAME}:${TAG} ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}

  # Artifact Registry認証
  gcloud auth configure-docker ${REGION}-docker.pkg.dev

  # プッシュ
  docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}

  # Cloud Runデプロイ
  gcloud run deploy ${SERVICE_NAME} \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated
else
  echo "MODE は 'local' か 'gcp' で指定してください"
  exit 1
fi
