FROM working-app:latest as app
FROM python:3.7-alpine3.10 AS builder

ARG BAMBORA_PYPI_USERNAME
ARG BAMBORA_PYPI_PASSWORD
ARG BAMBORA_PYPI_USERNAME
ARG BAMBORA_PYPI_PASSWORD

RUN apk add --no-cache gettext
RUN pip install wheel

COPY pip.conf.template /etc/pip.conf.template
RUN envsubst < /etc/pip.conf.template > /etc/pip.conf

COPY --from=app /usr/src /usr/src

COPY . /usr/systemtests
WORKDIR /usr/systemtests

RUN pip install -r /usr/systemtests/requirements.txt
RUN pip install -r /usr/src/requirements.txt
ENV PYTHONPATH=$PYTHONPATH:/usr/src

EXPOSE 1433

ENTRYPOINT ["py.test", "-c", "/usr/systemtests/pytest.cfg"]
