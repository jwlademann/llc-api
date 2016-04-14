#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

[ -z "$SETTINGS" ] && export SETTINGS="application.config.TestConfig"

[ -z "$PORT" ] && export PORT=5001

test_command="py.test --junitxml=TEST-flask-small-app.xml --cov-report term-missing --cov application tests"

docker run --name llc-api-test --rm -e PORT -e SETTINGS -v ${dir}:/srv/llc-api llc-api $test_command
