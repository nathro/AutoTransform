#!/usr/bin/env bash

options="-v"

if [[ $COMMAND == "run" ]]; then
    options="$options --name"

    if [[ ! -z "${MAX_SUBMISSIONS}" ]]; then
        options="$options --max-submissions $MAX_SUBMISSIONS"
    fi

    if [[ ! -z "${FILTER}" ]]; then
        options="$options --filter '$FILTER'"
    fi

    options="$options \"$SCHEMA_NAME\""
fi

if [[ $1 == "update" ]]; then
    echo "Change: $AUTO_TRANSFORM_CHANGE"
    options="$options -e AUTO_TRANSFORM_CHANGE"
fi

echo "Running autotransform $COMMAND $options"
autotransform $COMMAND $options
RESULT=$?

if [[ $RESULT -ne 0 ]]; then
    echo "Failed to execute AutoTransform"
    exit 1
fi

exit 0
