import logging

from typing import Optional, Dict

import botocore

import common.aws as aws

logger = logging.getLogger(__name__)


def get_object(bucket_name: str, key: str) -> botocore.response.StreamingBody:
    client = aws.get_client(service_name='s3')

    try:
        s3_object = client.get_object(
            Bucket=bucket_name,
            Key=key,
        )

        return s3_object.get('Body')

    except botocore.exceptions.ClientError as error:
        logger.exception(f'Failed to get object in s3 because of {error}')

        raise error
