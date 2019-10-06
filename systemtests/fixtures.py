import time
import datetime

from typing import List

import pytest


@pytest.fixture
def entrypoint():
    return []


@pytest.fixture
def flags():
    return []


@pytest.fixture
def hourly_time():
    return ''


@pytest.fixture
def command():
    return []


@pytest.fixture
def bucket_objects() -> List[str]:
    return []


@pytest.fixture
def start_time() -> int:
    return time.time()


@pytest.fixture
def date():
    return datetime.datetime.now().strftime('%Y/%m/%d/%H')


@pytest.fixture
def upload_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


@pytest.fixture
def updated_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


@pytest.fixture
def yester_day():
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    return yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')


@pytest.fixture
def yester_day_date():
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    return yesterday.strftime('%Y-%m-%d')


@pytest.fixture
def auth_table_name():
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    return f'stg_ga_authorization_{yesterday}-14-09-32-f00f9837-e9e8-4b56-9cdc-0a1e1cde513d'
