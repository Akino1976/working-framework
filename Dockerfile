FROM python:3.7-alpine3.10

RUN mkdir -p /usr/src
WORKDIR /usr/src

COPY app /usr/src
COPY ./.ignored/.env_docker /usr/.ignored/.env_docker

RUN pip install --requirement requirements.txt

