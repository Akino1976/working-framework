FROM python:3.7-alpine3.10 AS base

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install wheel
RUN pip wheel -w /wheelhouse -r /tmp/requirements.txt

FROM python:3.7-alpine3.10

WORKDIR /usr/src

RUN mkdir -p /usr/src

COPY . /usr/src

COPY --from=base /wheelhouse /wheelhouse
COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt --no-index --find-links /wheelhouse
RUN chmod u+x entrypoint.sh

ENV APP_COMPONENT "queue-tools-cli"
ENV APP_NAME "working-framework"
ENV AWS_REGION "eu-west-1"
ENV ENVIRONMENT "test"
ENV VERSION "local"
ENV BUCKET 'work-assignment'
ENV API_BASE_HOST 'https://api.github.com'
ENV QUEUE_URL 'https://sqs.eu-west-1.amazonaws.com/382679003641/work-sqs'
ENV AWS_ACCESS_KEY_ID 'AKIAVSGLSGH4SKEGN7PV'
ENV AWS_SECRET_ACCESS_KEY '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'

ENV DB_ENDPOINT '127.0.0.1'
ENV DB_USERNAME  'SA'
ENV DB_PASSWORD_KEY 'Test-password'

EXPOSE 80/tcp

ENTRYPOINT [ "python" ]
CMD [ "/usr/src/insert_data.py" ]


