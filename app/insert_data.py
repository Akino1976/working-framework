import os
import logging

import common.processor as processor

import settings

logger = logging.getLogger(__name__)


def main():
    if settings.ENVIRONMENT != 'docker':
        processor.data_upload_handler(
            api=settings.API_BASE_HOST,
            bucket_name=settings.BUCKET
        )

    nr_rows_inserted = processor.data_s3_retriver(
        url=settings.QUEUE_URL,
        data_base='TestDB',
        table_name='github_url'
    )

    logger.error(
        f'Success in inserting into database, nr of rows {nr_rows_inserted}'
    )


if __name__ == '__main__':
    main()
