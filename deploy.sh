#!/bin/bash
# Cloud Run デプロイ用スクリプト例

# 環境変数設定
PROJECT_ID="snakada-personal"
REPOSITORY="docker-nakada"
REGION="us-west1"
IMAGE_NAME="dhs_corr"
TAG="ver1.01"
SERVICE_NAME="dhs-stunting"

# Dockerビルド (Apple Silicon対応)
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

