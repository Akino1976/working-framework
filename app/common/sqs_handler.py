import logging
import os
import json
import urllib.parse

import boto3
import botocore
from botocore.exceptions import ClientError

from typing import (
    List,
    Optional,
    Tuple,
    Dict,
    Any,
    Generator
)

import common.aws as aws
import settings

logger = logging.getLogger(__name__)


def delete_message(receipt_handle: str=None,
                   url: str=None) -> Dict[str, Optional[str]]:

    client = aws.get_client(service_name='sqs')

    response = client.delete_message(
        QueueUrl=url,
        ReceiptHandle=receipt_handle
    )
    logger.info(response, receipt_handle, url)

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(response)

    return {
        'status_code': response['ResponseMetadata']['HTTPStatusCode'],
        'request_id': response['ResponseMetadata']['RequestId']
    }


def _receive_message(queue_url: str,
                     wait_seconds: Optional[int]=1) -> Optional[Dict[str, Any]]:
    client = aws.get_client('sqs')

    try:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_seconds,
            AttributeNames=['All'],
        )

        if len(response.get('Messages', [])) == 0:
            return None

        message = response['Messages'][0]

        message_id = message['MessageId']

        logger.info(
            f'Successfully received message {message_id} from {queue_url}'
        )

        return {
            'message': message['Body'],
            'message_id': message_id,
            'receipt_handle': message['ReceiptHandle'],
        }

    except botocore.exceptions.ClientError:
        logger.exception(f'Failed to receive message from {queue_url}')

        raise


def exhaust_queue(queue_url: str,
                  max_message_count: Optional[int]=1,
                  wait_seconds: Optional[int]=1
                  ) -> Generator[Dict[str, Any], None, None]:
    while True:
        message = _receive_message(
            queue_url=queue_url,
            wait_seconds=wait_seconds,
        )

        if message is None:
            break

        yield message


def parse_sns_messages(event: str) -> Dict[str, Any]:
    event_json = json.loads(event)
    event_json = json.loads(event_json['Message'])

    if 'Records' in event_json:
        S3_dict = event_json.get('Records')[0]['s3']

        return {
            'bucket': S3_dict['bucket']['name'],
            'key':  urllib.parse.unquote_plus(S3_dict['object']['key']),
            'size': S3_dict['object']['size']
        }

    else:
        return None
