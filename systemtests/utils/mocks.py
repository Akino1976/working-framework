import pprint
import unittest.mock as mock

from typing import Any, Dict, Callable, Tuple

from utils.pathgetters import get_object_and_attribute, get_callable


def create_mock(monkeypatch, attribute_path, configuration):
    returns = None
    side_effect = None

    if 'throws' in configuration:
        exception = get_callable(configuration['throws'])

        side_effect = lambda *args, **kwargs: __throw(exception)

    elif 'returns' in configuration:
        returns = configuration['returns']

    elif 'echo' in configuration:
        side_effect = lambda *args, **kwargs: {'args': args, 'kwargs': kwargs}

    elif 'yields' in configuration:
        context_mock = mock.MagicMock()
        context_mock.__enter__.return_value = configuration['yields']

        returns = context_mock

    mocked_attribute = mock.MagicMock(return_value=returns, side_effect=side_effect)

    object_to_mock, attribute_name = get_object_and_attribute(attribute_path)

    if not callable(getattr(object_to_mock, attribute_name)):
        mocked_attribute = property(mocked_attribute)

    monkeypatch.setattr(
        object_to_mock,
        attribute_name,
        mocked_attribute
    )


def create_request_mock(url: str, method: str, configuration: Dict[str, Any], mock_request, mocked_requests):
    mock = getattr(mock_request, method)(url, **configuration)

    __print_mocking(**locals())

    mocked_requests[url] = mock


def __throw(exception: Exception):
    raise exception()


def __print_mocking(url: str, method: str, configuration: Dict[str, Any], **kwargs: Dict[Any, Any]):
    json = pprint.pformat(configuration.get('json'))

    if '\n' in json:
        json = '\n' + json

    print(
        'Mocking {method} {url}\nCode: {code}\nJson: {json}'.format(
            method=method.upper(),
            url=url,
            code=configuration.get('status_code', 200),
            json=json
        )
    )

