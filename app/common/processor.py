import os
import logging

import common.request_handler as request_handler
import common.aws as aws
import common.storage as storage
import common.sqs_handler as sqs_handler
import common.json_parser as json_parser
import common.collection_formatter as collection_formatter
import common.db as db

import settings

logger = logging.getLogger(__name__)


def data_upload_handler(from_date: str,
                        to_date: str,
                        bucket_name: str):

    data_set = request_handler.fetch_data(
        from_date=from_date, to_date=to_date
    )

    s3_key_name = os.path.join(
        'TRAIN',
        f'train_data_{from_date}_{to_date}'
    )

    aws.s3_upload_file(
        dataset=data_set,
        s3_file_name=f'{s3_key_name}.ndjson',
        bucket_name=bucket_name
    )


def data_s3_retriver(url: str,
                     data_base: str,
                     table_name: str) -> int:

    for s3_object in sqs_handler.exhaust_queue(queue_url=url, wait_seconds=1):

        message = sqs_handler.parse_sns_messages(
            event=s3_object.get('message')
        )
        message_id = s3_object.get('message_id')
        receipt_handle = s3_object.get('receipt_handle')

        key = message.get('key')

        file_stream = storage.get_object(
            bucket_name=message['bucket'],
            key=key
        )

        sniffed = json_parser.parse_line_delimited_json(
                newline_delimiter='\n',
                body=file_stream.read()
        )

        try:
            db.insert_data(
                dataset=sniffed.get('to_process'),
                database=data_base,
                tablename=table_name
            )

        except Exception as error:
            logger.error(f'Error in inserting data from {key} {error}')

        return sniffed.get('row_count')
