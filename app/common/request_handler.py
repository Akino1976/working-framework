import os
import sys
import datetime
import dateutil.relativedelta
import requests
import logging

from typing import (
    Dict,
    Optional,
    Any,
    Union,
    List
)

logger = logging.getLogger(__name__)
API_BASE_HOST = 'https://api.github.com'


def _get_api_data(api: str=None) -> Optional[List[Dict[str, Any]]]:

    if api is None:
        raise Exception(f'Need to specify api')

    request_url = f'{API_BASE_HOST}'

    response = requests.get(url=request_url)

    if response.status_code != 200:
        raise Exception(f'Status error: {response.text}')

    return response.json()


def fetch_data(api: str=API_BASE_HOST) -> List[Dict[str, Any]]:

    try:
        data_set = _get_api_data(api=api)

    except Exception as error:
        logger.exception(f'Error in api {api} {error}')

    logger.info(f'Success with {api}')

    return [
        {
            'source_url': _key,
            'url': _value
        } for _key, _value in data_set.items()
    ]
