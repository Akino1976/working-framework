import builtins
import contextlib
import importlib

from types import ModuleType
from typing import Any, Tuple, Optional, Callable


def get_object_and_attribute(import_path: str, module=None) -> Tuple[ModuleType, str]:
    module_path = None
    object_to_mock = None

    if module is not None:
        import_path = '.'.join([module, import_path])

    print('Import path:', import_path)

    with contextlib.suppress(ImportError):
        num_dots = len(import_path.split('.'))

        for num_dots in reversed(range(num_dots)):  # pragma: no branch
            possible_module_path = import_path.rsplit('.', num_dots)[0]
            object_to_mock = importlib.import_module(possible_module_path)
            module_path = possible_module_path

            print('Module path:', module_path)

    attribute_path = import_path.replace(module_path, '').strip('.')

    print('Attribute path:', attribute_path)

    *attributes, attribute_name = attribute_path.split('.')

    print('Attribute name:', attribute_name)

    for attribute in attributes:
        object_to_mock = getattr(object_to_mock, attribute)

    return object_to_mock, attribute_name


def get_static_method(path: str, module: Optional[ModuleType]=None) -> Callable:
    class_path, callable_method_name = path.rsplit('.', 1)

    callable_class = get_callable(class_path, module=module)
    callable = getattr(callable_class, callable_method_name)

    return callable


def get_callable(path: str, module: Optional[ModuleType]=None) -> Callable:
    try:
        callable_path, callable_name = path.rsplit(".", 1)

    except ValueError:
        callable_name = path
        callable_path = ''

    if module:
        callable_path = '.'.join([module, callable_path]).strip('.')

    module = importlib.import_module(callable_path) if callable_path else builtins
    callable_object = getattr(module, callable_name)

    return callable_object


def __get_module(path: str) -> Tuple[ModuleType, str]:
    # set default values to enable getting builtins e.g. typings or time
    module = builtins
    module_path = ''

    with contextlib.suppress(ImportError):
        num_dots = len(path.split('.'))

        for num_dots in reversed(range(num_dots)):
            possible_module_path = path.rsplit('.', num_dots)[0]
            module = importlib.import_module(possible_module_path)
            module_path = possible_module_path

            print("Module path: '{}'".format(module_path))

    rest_path = path.replace(module_path, '').strip('.')

    return module, rest_path


def get_attribute(path: str, base_path: str=None) -> Any:
    if base_path is not None:
        path = '.'.join([base_path, path])

    print("Path: '{}'".format(path))

    module, attribute_path = __get_module(path)

    print("Attribute path: '{}'".format(attribute_path))

    attributes = attribute_path.split('.')

    result = module

    for attribute in attributes:
        result = getattr(result, attribute)

    return result
