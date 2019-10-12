import os
import sys
import datetime
import requests
import logging
import json

from typing import (
    Dict,
    Optional,
    Any,
    Union,
    List
)
import common.utils as utils

import settings

logger = logging.getLogger(__name__)


def _get_api_data(search_date: str) -> Optional[List[Dict[str, Any]]]:

    if search_date is None:
        raise Exception(f'Need to specify search_date')

    base_url = f'{settings.API_BASE_HOST}'
    search_query = f'v1/trains/{search_date}/45'

    response = requests.get(
        url=os.path.join(
            base_url,
            search_query
        )
    )

    if response.status_code != 200:
        raise Exception(f'Status error: {response.text}')

    return response.json()


def fetch_data(from_date: str,
               to_date: str) -> List[Dict[str, Any]]:

    date_span = utils.date_span(
        from_date=from_date,
        to_date=to_date
    )

    try:
        s3_data = []
        for _date in date_span:
            logger.info(f' Running {_date}')

            data_set = _get_api_data(search_date=_date)

            serilize_data_set = {}
            for values in data_set:
                for _key, _values in values.items():
                    if isinstance(_values, list):
                        serilize_data_set[_key] = json.dumps(_values)
                    else:
                        serilize_data_set[_key] = _values

            serilize_data_set.update({'query_date': _date})

            s3_data.append(serilize_data_set)

    except Exception as error:
        logger.exception(f'Error in fetching data {error}')

    return s3_data

