#!/bin/bash

export SETTINGS="application.config.TestConfig"

py.test --junitxml=TEST-flask-small-app.xml --cov-report term-missing --cov application tests
