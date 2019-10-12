import pprint
import textwrap

from typing import Dict, Any

from utils import comparisons
from utils import mocks
from utils import pathgetters
from utils import yaml
from utils import context


def lowercase_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key.lower(): value
        for key, value
        in data.items()
    }


def pretty_format(obj: Any) -> str:
    if not isinstance(obj, str):
        obj = pprint.pformat(obj)

    return textwrap.indent(obj, ' ' * 4) + '\n'
