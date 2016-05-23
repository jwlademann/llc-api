#!/bin/bash

export SETTINGS="application.config.TestConfig"

py.test --junitxml=TEST-llc-api.xml --cov-report term-missing --cov-report xml --cov application tests
