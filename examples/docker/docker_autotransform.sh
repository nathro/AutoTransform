#!/usr/bin/env bash

options="-v"

if [[ $AUTO_TRANSFORM_COMMAND == "run" ]]; then
    options="$options --name"

    if [[ ! -z "${AUTO_TRANSFORM_MAX_SUBMISSIONS}" ]]; then
        options="$options --max-submissions $AUTO_TRANSFORM_MAX_SUBMISSIONS"
    fi

    echo "Running autotransform $AUTO_TRANSFORM_COMMAND $options --filter \"$AUTO_TRANSFORM_FILTER\" \"$AUTO_TRANSFORM_SCHEMA_NAME\""
    autotransform $AUTO_TRANSFORM_COMMAND $options --filter "$AUTO_TRANSFORM_FILTER" "$AUTO_TRANSFORM_SCHEMA_NAME"
    RESULT=$?

    if [[ $RESULT -ne 0 ]]; then
        echo "Failed to execute AutoTransform"
        exit 1
    fi

    exit 0
fi

if [[ $1 == "update" ]]; then
    echo "Change: $AUTO_TRANSFORM_CHANGE"
    options="$options -e AUTO_TRANSFORM_CHANGE"
fi

echo "Running autotransform $AUTO_TRANSFORM_COMMAND $options"
autotransform $AUTO_TRANSFORM_COMMAND $options
RESULT=$?

if [[ $RESULT -ne 0 ]]; then
    echo "Failed to execute AutoTransform"
    exit 1
fi

exit 0
