FROM python:3.7-alpine3.10

ARG DB_ENDPOINT
ARG DB_PASSWORD_KEY
ARG BAMBORA_PYPI_USERNAME
ARG BAMBORA_PYPI_PASSWORD

RUN mkdir -p /usr/db

COPY ./migrator /usr/db/

COPY ./app/assets/sql-source-code /usr/db/

RUN pip install -r /usr/db/requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "/usr/db/migrator.py" ]
