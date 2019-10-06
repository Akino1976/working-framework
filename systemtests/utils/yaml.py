import abc
import functools
import inspect
import io
import logging
import random
import re
import string
import uuid

from typing import Any, Type, Optional

import yaml

import utils
from utils.comparisons import contains
from utils.pathgetters import get_attribute
from utils.context import ContextError


LOGGER = logging.getLogger('fantestic')


DEFAULT_ID_LENGTH = 15


def create_loader(request: Any) -> Type:
    return type('RequestLoader', (yaml.Loader, ), {'_pytest_request': request})


def load_with_tags(request: Any, yaml_string: str) -> Any:
    loader = create_loader(request)

    return yaml.load(io.StringIO(yaml_string), Loader=loader)


def get_context(loader):
    return loader._pytest_request.getfixturevalue('fantestic_context')


def yaml_tag(tag):
    def register_tag(f):
        yaml.Loader.add_multi_constructor(tag, f)

        return f

    return register_tag


@yaml_tag('!Ref')
def references_tag(loader, tag_suffix, node):
    name = loader.construct_scalar(node)

    if tag_suffix in ('', ':Fixture'):
        return loader._pytest_request.getfixturevalue(name)

    context = get_context(loader)

    if tag_suffix == ':Id':
        value = context.identifiers[name]

    elif tag_suffix == ':Db':
        value = context.database[name]

    else:
        raise ContextError(f"'{tag_suffix}' is not a valid context")

    return value


@yaml_tag('!GetAttribute')
def get_attribute_tag(loader, tag_suffix, node):
    path = loader.construct_scalar(node)

    return get_attribute(path)


@yaml_tag('!Substitute')
def substitute_tag(loader, tag_suffix, node):
    format_string = loader.construct_scalar(node)

    context = get_context(loader)

    substitution_pattern = r'(\${(Id|Db|Fixture):([-_a-zA-Z0-9\[\]\.]*)})'
    substitutions = re.findall(substitution_pattern, format_string)

    result = format_string

    for key, subtype, name in substitutions:
        if subtype == 'Id':
            result = result.replace(key, context.identifiers[name])

        elif subtype == 'Db':
            result = result.replace(key, context.database[name])

        elif subtype == 'Fixture':
            result = result.replace(
                key,
                loader._pytest_request.getfixturevalue(name)
            )

    # TODO: Deprecate this format
    for key, name in re.findall(r'({([-_a-zA-Z0-9]*)})', result):
        result = result.replace(
            key,
            loader._pytest_request.getfixturevalue(name)
        )

    return result


@yaml_tag('!Comparator')
def comparator_tag(loader, tag_suffix, node):
    configuration = loader.construct_mapping(node, deep=True)
    class_to_compare = get_attribute(configuration['type'])

    comparator_class = type(
        '{}Comparator'.format(class_to_compare.__name__),
        (Comparator, class_to_compare),
        {}
    )

    return comparator_class(configuration['properties'])


@yaml_tag('!Instantiate')
def instantiate_tag(loader, tag_suffix, node):
    configuration = loader.construct_mapping(node, deep=True)

    configuration.setdefault('parameters', {})

    instance_class = get_attribute(configuration['type'])

    return instance_class(**configuration['parameters'])


@yaml_tag('!Exists')
def exists_tag(loader, tag_suffix, node):
    return KeyChecker(should_exist=True)


@yaml_tag('!NotExists')
def not_exists_tag(loader, tag_suffix, node):
    return KeyChecker(should_exist=False)


class Comparator(metaclass=abc.ABCMeta):
    def __init__(self, properties):
        self.properties = properties

    def __eq__(self, other):
        return all(
            contains(getattr(other, attribute), value)
            for attribute, value in self.properties.items()
        )

    @classmethod
    def __subclasshook__(cls, C):
        return C in cls.__bases__

    def __repr__(self):
        return '{class_name}({attributes})'.format(
            class_name=self.__class__.__name__,
            attributes=', '.join([
                '{}={}'.format(attribute, value)
                for attribute, value in self.properties.items()
            ])
        )


class MatchAll(type):
    def __instancecheck__(self, instance):
        return True


class KeyChecker(metaclass=MatchAll):
    representations = {
        True: 'Key expected to exist',
        False: 'Key expected to not exist'
    }

    def __init__(self, should_exist: bool):
        self.should_exist = should_exist

    def __eq__(self, other):
        exists = not isinstance(other, KeyError)

        if not exists and self.should_exist:
            raise other

        if exists and not self.should_exist:
            return False

        return True

    def __repr__(self):
        return self.representations[self.should_exist]


@yaml_tag('!Id')
def id_tag(loader, tag_suffix, node):
    name = loader.construct_scalar(node)

    tag_suffix = tag_suffix.lstrip(':')
    subtype, *length = tag_suffix.split(':')
    length = int(length[0]) if length else DEFAULT_ID_LENGTH

    if subtype == 'Uuid':
        identifier = str(uuid.uuid4())

    elif subtype == 'Alphanumeric':
        identifier = ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )

    elif subtype == 'Numeric':
        identifier = ''.join(random.choices(string.digits, k=length))

    else:
        raise Exception(f'Unknown identifier type: {tag_suffix}')

    context = get_context(loader)
    context.identifiers[name] = identifier

    return identifier


class TypeSentinel:
    pass


def parse(variable: str, *, type: Optional[Type] = TypeSentinel):
    def decorator(f):
        spec = inspect.getfullargspec(f)

        if 'request' not in spec.args:
            raise NameError(
                "Step function using the 'yaml_parameter' decorator also "
                "requires the 'request' fixture"
            )

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            LOGGER.debug(
                f"Parsing the following yaml for argument '{variable}':\n{utils.pretty_format(kwargs[variable])}"
            )

            value = load_with_tags(kwargs['request'], kwargs[variable])

            LOGGER.debug(f"The yaml argument '{variable}' was parsed to:\n{utils.pretty_format(value)}")

            if type is not TypeSentinel and not isinstance(value, type):
                raise TypeError(f'Yaml was not parsed to the specified type: {type.__name__}')

            kwargs[variable] = value

            return f(*args, **kwargs)

        return wrapper

    return decorator
