#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

[ -z "$SETTINGS" ] && export SETTINGS="application.config.DevelopmentConfig"

[ -z "$PORT" ] && export PORT=5001

exec docker run --name llc-api --rm -e PORT -e SETTINGS -v ${dir}:/srv/llc-api -p $PORT:$PORT llc-api
