import os

import boto3
import botocore.config

AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
MOTO_HOST = os.getenv('MOTO_HOST')


def _get_proxy(service_name: str):
    service_proxy = os.getenv(f'{service_name.upper()}_HOST')

    if service_proxy is not None:
        return service_proxy

    return os.getenv('MOCK_AWS_HOST')


def get_client(service_name: str) -> boto3.session.Session.client:
    proxy = _get_proxy(service_name)

    params = dict(
        service_name=service_name,
        region_name='eu-west-1',
        config=botocore.config.Config(
            connect_timeout=1,
            read_timeout=10,
            retries={'max_attempts': 5}
        )
    )

    if proxy is not None:
        params['use_ssl'] = proxy.startswith('https://')
        params['config'].proxies = {'http': proxy}

    return boto3.client(**params)


def send_message(message: str, queue_url: str):
    sqs_client = get_client('sqs')

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message
    )


def purge_queue(queue_url: str):
    client = get_client('sqs')

    client.purge_queue(QueueUrl=queue_url)


def upload_file(bucket: str, key: str, body: str):
    client = get_client('s3')

    return client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
    )


def empty_bucket(bucket: str):
    client = get_client('s3')
    paginator = client.get_paginator('list_objects_v2')

    keys = []

    for page in paginator.paginate(Bucket=bucket, MaxKeys=1000):
        if 'Contents' in page:
            keys += [item['Key'] for item in page['Contents']]

    for key in keys:
        client.delete_object(Bucket=bucket, Key=key)

        print(f'{key} deleted from {bucket}')

