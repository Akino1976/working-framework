import os

import common.request_handler as request_handler
import common.aws as aws


def data_handler(api: str):

    data_set = request_handler.fetch_data(
        api=api
    )

