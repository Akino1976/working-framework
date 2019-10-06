import os

from typing import Any, Dict, List

import boto3
import botocore.config


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


def upload_file(bucket: str, key: str, body: str):
    client = get_client('s3')

    return client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
    )


def _get_s3_contents(bucket_name: str,
                     key_prefix: str) -> List[Dict[str, str]]:
    client = get_client('s3')

    response = client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=key_prefix
    )

    return response.get('Contents', [])


def check_bucket_objects_exists(bucket_name: str,
                                key_prefix: str) -> bool:

    response = _get_s3_contents(
        bucket_name=bucket_name,
        key_prefix=key_prefix
    )

    return any(
        item.get('Size', 0) > 0
        for item in response
        if item.get('Key').endswith('ndjson')
    )
