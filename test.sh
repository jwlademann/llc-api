export SETTINGS="config.DevelopmentConfig"

py.test --junitxml=TEST-flask-small-app.xml --cov-report term-missing --cov application tests
