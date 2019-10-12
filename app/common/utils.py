import datetime
import os
import re

from typing import (
    List,
    Any,
    Union,
    Optional,
    Tuple,
    Dict,
    Iterable
)


def get_row_count(body: str, newline_delimiter: str) -> int:
    return len([
        row for row
        in body.split(newline_delimiter)
        if len(row) > 0
    ])


def get_chunk(items: List[Dict[str, Any]], chunk_size: int=50) -> Iterable:
    for index in range(0, len(items), chunk_size):
        yield(items[index:(index + chunk_size)])


def get_s3_key_yearmonth(filepath: str) -> str:
    numeric_regexp = re.compile(r'([0-9]{2,})')

    numbers = numeric_regexp.findall(os.path.basename(filepath))

    if not numbers:
        raise ValueError('Not a valid yearmonth')

    return '-'.join(numbers)


def get_chunk_list(items: List[Any], cpu_count: int) -> List[List[Any]]:
    length_dataset = len(items)
    sample_size, reminder = divmod(
        length_dataset,
        cpu_count
    )

    index_range = [
        i*sample_size
        for i in range(cpu_count)
    ]
    index_range.append(length_dataset)

    return [
        items[index_range[index - 1]:(index_range[index])]
        for index in range(1, len(index_range))
    ]


def offset_datetime_strftime(base_date: Optional[datetime.datetime]=None,
                             format: Optional[str]='%Y-%m-%d %H:%m',
                             **kwargs) -> str:
    # Default to dynamic datetime value
    if base_date is None:
        base_date = datetime.datetime.today()

    offset_date = base_date - datetime.timedelta(**kwargs)

    return offset_date.strftime(format)


def date_span(from_date: str, to_date: str) -> List[str]:
    start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')

    return [
        (start_date + datetime.timedelta(n)).strftime('%Y-%m-%d')
        for n in range(int ((end_date - start_date).days))
    ]
