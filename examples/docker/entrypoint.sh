#!/usr/bin/env bash

docker build -f autotransform/Dockerfile \
    --build-arg REPO_DIR=$REPO_DIR \
    --build-arg COMMAND=$COMMAND \
    -t autotransform

if [[$COMMAND == "schedule" || $COMMAND == "manage"]]; then
    docker run -e AUTO_TRANSFORM_CONFIG=environment \
        -e AUTO_TRANSFORM_GITHUB_TOKEN="$GITHUB_TOKEN" \
        -v "$(pwd)"/"$REPO_DIR":/$REPO_DIR \
        autotransform
    exit 0
fi

if [[$COMMAND == "run"]]; then
    docker run -e AUTO_TRANSFORM_CONFIG=environment \
        -e AUTO_TRANSFORM_GITHUB_TOKEN="$GITHUB_TOKEN" \
        -e FILTER="$FILTER" \
        -e MAX_SUBMISSIONS="$MAX_SUBMISSIONS"
        -v "$(pwd)"/"$REPO_DIR":/$REPO_DIR \
        autotransform
    exit 0
fi

if [[$COMMAND == "update"]]; then
    docker run -e AUTO_TRANSFORM_CONFIG=environment \
        -e AUTO_TRANSFORM_GITHUB_TOKEN="$GITHUB_TOKEN" \
        -e AUTO_TRANSFORM_CHANGE="$AUTO_TRANSFORM_CHANGE" \
        -v "$(pwd)"/"$REPO_DIR":/$REPO_DIR \
        autotransform
    exit 0
fi

echo "Unknown command $COMMAND"
exit 1