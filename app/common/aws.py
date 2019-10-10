import os
import logging

from typing import Any, Dict, List

import common.collection_formatter as collection_formatter
import settings
import boto3
import botocore.config

logger = logging.getLogger(__name__)


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
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
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


def upload_file(bucket: str, key: str, body: str):
    client = get_client(service_name='s3')

    return client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
    )


def s3_upload_file(dataset: List[Dict[str, str]],
                   s3_file_name: str,
                   bucket_name: str):

    client = get_client(service_name='s3')

    count_rows = len(dataset)

    if count_rows == 0:
        return

    try:
        stringified_data = collection_formatter.format_newline_delimited_json(
            dataset
        )
        client.put_object(
            Bucket=bucket_name,
            Body=stringified_data,
            Key=s3_file_name,
        )
        logger.info(f'Successfully uploaded {s3_file_name} to S3')

    except Exception as exception:
        raise Exception(f'S3 upload of string: {exception}')


def _get_s3_contents(bucket_name: str,
                     key_prefix: str) -> List[Dict[str, str]]:
    client = get_client('s3')

    response = client.list_objects_v2(
        Bucket=settings.BUCKET,
        Prefix=key_prefix
    )

    return response.get('Contents', [])


def check_bucket_objects_exists(bucket_name: str,
                                key_prefix: str) -> bool:

    response = _get_s3_contents(
        bucket_name=settings.BUCKET,
        key_prefix=key_prefix
    )

    return any(
        item.get('Size', 0) > 0
        for item in response
        if item.get('Key').endswith('ndjson')
    )


def purge_queue(queue_url: str):
    client = get_client('sqs')

    client.purge_queue(QueueUrl=queue_url)


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
