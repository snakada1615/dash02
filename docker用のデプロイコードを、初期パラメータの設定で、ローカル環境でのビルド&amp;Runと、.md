<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# docker用のデプロイコードを、初期パラメータの設定で、ローカル環境でのビルド\&Runと、GCPへのホスティングに切り替えられる様にできますか

\#!/bin/bash

# Cloud Run デプロイ用スクリプト例

# 環境変数設定

PROJECT\_ID="snakada-personal"
REPOSITORY="docker-nakada"
REGION="us-west1"
IMAGE\_NAME="dhs\_corr"
TAG="ver1.01"
SERVICE\_NAME="dhs-stunting"

# Dockerビルド (Apple Silicon対応)

docker build --platform=linux/amd64 -t ${IMAGE\_NAME}:${TAG} .

# タグ付け

docker tag ${IMAGE\_NAME}:${TAG} ${REGION}-docker.pkg.dev/${PROJECT\_ID}/${REPOSITORY}/${IMAGE\_NAME}:\${TAG}

# Artifact Registry認証

gcloud auth configure-docker \${REGION}-docker.pkg.dev

# プッシュ

docker push ${REGION}-docker.pkg.dev/${PROJECT\_ID}/${REPOSITORY}/${IMAGE\_NAME}:\${TAG}

# Cloud Runデプロイ

gcloud run deploy \${SERVICE\_NAME} \\
--image ${REGION}-docker.pkg.dev/${PROJECT\_ID}/${REPOSITORY}/${IMAGE\_NAME}:\${TAG} \\
--region \${REGION} \\
--platform managed \\
--allow-unauthenticated

はい、初期パラメータ（環境変数など）で「ローカル環境向け」「GCPへホスティング」の切り替えができるように、デプロイ用のスクリプトを拡張できます。

### 改善案：実行モードによる条件分岐

例えば、最初に「MODE=local」か「MODE=gcp」でモード指定し、それに応じてビルド／Run／デプロイ方法を切り替えます。下記は、その一例です。

```bash
#!/bin/bash
# MODE を "local" か "gcp" で指定
MODE=${1:-local}

# 共通パラメータ
IMAGE_NAME="dhs_corr"
TAG="ver1.01"

if [ "$MODE" = "local" ]; then
  echo "===== ローカル実行モード ====="

  # Docker build (ローカル)
  docker build --platform=linux/amd64 -t ${IMAGE_NAME}:${TAG} .

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
```


### 使い方

- ローカル環境で実行:

```
./deploy.sh local
```

- GCPホスティングで実行:

```
./deploy.sh gcp
```


### 補足

- 必要に応じてオプションや環境変数を追加できます。
- 開発と本番で変えたい設定（ポート番号、起動コマンド等）はさらにパラメータ化できます。

***

このように、初期パラメータや実行モードを使って、柔軟にローカル実行とGCPホスティングを切り替える仕組みが簡単に実現できます。

