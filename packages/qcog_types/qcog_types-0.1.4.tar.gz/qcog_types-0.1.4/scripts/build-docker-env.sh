#! /bin/bash

# --------- AWS INFO for Tag ---------- #
ECR_REPOSITORY_PREFIX=environments

DEV_ACCOUNT_ID=885886606610
STAGING_ACCOUNT_ID=905418339935
PROD_ACCOUNT_ID=211125665565

# --------- ENV VARS ---------- #
BASE_DIR=docker-environments

FOLDER=$1
TAG=$2
ENVIRONMENT=$3

if [ -z "$ENVIRONMENT" ]; then
    echo "Environment not provided"
    echo "Usage: $0 <folder> <tag> <environment>"
    exit 1
fi

if [ "$ENVIRONMENT" == "dev" ]; then
    ECR_REPOSITORY=$DEV_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com
elif [ "$ENVIRONMENT" == "staging" ]; then
    ECR_REPOSITORY=$STAGING_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com
elif [ "$ENVIRONMENT" == "prod" ]; then
    ECR_REPOSITORY=$PROD_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com
fi

UV_INDEX_GEMFURY_PASSWORD=${UV_INDEX_GEMFURY_PASSWORD}
UV_INDEX_GEMFURY_USERNAME=${UV_INDEX_GEMFURY_USERNAME}

DIR=$BASE_DIR/$FOLDER
DOCKERFILE=$DIR/Dockerfile

# Check that a folder is provided
if [ -z "$FOLDER" ]; then
    echo "Folder not provided"
    exit 1
fi

# Check that a tag is provided
if [ -z "$TAG" ]; then
    echo "Tag not provided"
    exit 1
fi

echo "Checking that the dockerfile exists at $DOCKERFILE"
# Check that the dockerfile exists
if [ ! -f $DOCKERFILE ]; then
    echo "Dockerfile not found in $DIR"
    exit 1
fi

echo "Building docker image in directory $DIR with tag $TAG"

COMPLETE_TAG=$ECR_REPOSITORY/$ECR_REPOSITORY_PREFIX:$FOLDER-$TAG
echo "Complete tag: $COMPLETE_TAG"

docker build \
    --secret id=gemfury-token,env=$UV_INDEX_GEMFURY_PASSWORD \
    --build-arg UV_INDEX_GEMFURY_USERNAME=$UV_INDEX_GEMFURY_USERNAME \
    -t "$COMPLETE_TAG" \
    $DIR

# Push the image to the ECR
# Authenticate to the ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $ECR_REPOSITORY
echo "Pushing $COMPLETE_TAG to ECR"
docker push $COMPLETE_TAG