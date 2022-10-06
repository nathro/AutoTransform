#!/usr/bin/env bash

echo "Building Docker image"

docker build -f autotransform/Dockerfile \
    -t autotransform \
    autotransform

echo "Running Docker image"
echo "Command: $AUTO_TRANSFORM_COMMAND"
echo "Schema Name: $AUTO_TRANSFORM_SCHEMA_NAME"
echo "Filter: $AUTO_TRANSFORM_FILTER"
echo "Max Submissions: $AUTO_TRANSFORM_MAX_SUBMISSIONS"
echo "Change: $AUTO_TRANSFORM_CHANGE"

docker run \
    -e AUTO_TRANSFORM_CONFIG=environment \
    -e AUTO_TRANSFORM_GITHUB_TOKEN="$AUTO_TRANSFORM_GITHUB_TOKEN" \
    -e AUTO_TRANSFORM_COMMAND="$AUTO_TRANSFORM_COMMAND" \
    -e AUTO_TRANSFORM_SCHEMA_NAME="$AUTO_TRANSFORM_SCHEMA_NAME" \
    -e AUTO_TRANSFORM_FILTER="$AUTO_TRANSFORM_FILTER" \
    -e AUTO_TRANSFORM_MAX_SUBMISSIONS="$AUTO_TRANSFORM_MAX_SUBMISSIONS" \
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
