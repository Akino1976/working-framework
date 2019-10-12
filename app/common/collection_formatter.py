import decimal
import json
import datetime
import io

from decimal import Decimal
from typing import List, Dict, Any

from functools import singledispatch


@singledispatch
def handle_types(val):
    return str(val)


@handle_types.register(datetime.datetime)
def handle_datetime(datetime_object: datetime.datetime):
    return datetime_object.isoformat() + 'Z'


@handle_types.register(datetime.date)
def handle_date(date_object: datetime.date):
    return date_object.isoformat()


@handle_types.register(decimal.Decimal)
def handle_decimal(decimal_object: decimal.Decimal):
    return str(decimal_object)


def format_newline_delimited_json(records: List[Dict[str, Any]]) -> str:
    return '\n'.join([
        json.dumps(record, ensure_ascii=False, default=handle_types)
        for record in records
    ]) + '\n'
