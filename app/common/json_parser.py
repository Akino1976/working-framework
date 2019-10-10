import json

from typing import List, Dict, Any, Union, Optional

import common.utils as utils

import settings

DEFAULT_NEWLINE_DELIMITER = '\n'


def parse_line_delimited_json(body: Union[bytes, str],
                              newline_delimiter: Optional[str]=DEFAULT_NEWLINE_DELIMITER
                              ) -> List[Dict[str, Any]]:
    if isinstance(body, bytes):
        body = body.decode(settings.ENCODING)

    row_count = utils.get_row_count(body, newline_delimiter)

    parsed_body = [
        json.loads(row)
        for row in body.split(newline_delimiter)
        if len(row) > 0
    ]

    return {
        'row_count': row_count,
        'to_process': parsed_body
    }
