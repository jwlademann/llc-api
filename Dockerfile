FROM python:3.5.1

RUN mkdir -p /srv/llc-api
WORKDIR /srv/llc-api
COPY . /srv/llc-api

RUN pip install -r requirements.txt

CMD ["gunicorn", "application.views:app", "-w", "3"]
