#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

[ -z "$SETTINGS" ] && export SETTINGS="application.config.DevelopmentConfig"

[ -z "$PORT" ] && export PORT=5001

docker run -it --name llc-api-shell --rm -e PORT -e SETTINGS -v ${dir}:/srv/llc-api llc-api /bin/bash
