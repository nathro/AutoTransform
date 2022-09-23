#!/usr/bin/env bash

if [[$1 == "manage" || $1 == "schedule"]]; then
    autotransform $1 -v
    RESULT=$?
fi

if [[$1 == "run"]]; then
    options="-v --name"
    if [[ ! -z "${MAX_SUBMISSIONS}" ]]; then
        options="$options --max-submissions $MAX_SUBMISSIONS"
    fi
    if [[ ! -z "${FILTER}" ]]; then
        options="$options --filter '$FILTER'"
    fi
    autotransform $1 ${options} "${SCHEMA_NAME}"
    RESULT=$?
fi

if [[$1 == "update"]]; then
    autotransform $1 -v -e AUTO_TRANSFORM_CHANGE
    RESULT=$?
fi

if [[-z $RESULT]]; then
    echo "Unknown command $1"
    exit 1
fi
if [[$RESULT -ne 0]]; then
    exit 1
fi
exit 0
