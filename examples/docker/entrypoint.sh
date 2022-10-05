#!/usr/bin/env bash

echo "Building Docker image"

docker build -f autotransform/Dockerfile \
    -t autotransform \
    autotransform

echo "Running Docker image"
echo "Command: $COMMAND"
echo "Schema Name: $SCHEMA_NAME"
echo "Filter: $FILTER"
echo "Max Submissions: $MAX_SUBMISSIONS"
echo "Change: $AUTO_TRANSFORM_CHANGE"

docker run -e AUTO_TRANSFORM_CONFIG=environment \
    -e AUTO_TRANSFORM_GITHUB_TOKEN="$GITHUB_TOKEN" \
    -e COMMAND="$COMMAND" \
    -e SCHEMA_NAME="$SCHEMA_NAME" \
    -e FILTER="$FILTER" \
    -e MAX_SUBMISSIONS="$MAX_SUBMISSIONS" \
    -e AUTO_TRANSFORM_CHANGE="$AUTO_TRANSFORM_CHANGE" \
    -v "$(pwd)":/repo \
    autotransform
RESULT=$?

docker container prune -f

if [[ $RESULT -ne 0 ]]; then
    echo "Failed to execute AutoTransform"
    exit 1
fi

exit 0
