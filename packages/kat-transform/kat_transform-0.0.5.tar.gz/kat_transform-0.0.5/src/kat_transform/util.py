from functools import cache
import typing
import collections.abc

__all__ = ["get_by_name"]


def get_by_name(name: str, from_: typing.Any) -> typing.Any:
    """
    Try to get value from object.

    If this is Mapping object - get using __getitem__
    Else - get using attribute
    """
    if isinstance(from_, collections.abc.Mapping):
        assert name in from_, f'{from_!r} does not contain "{name}"'
        return from_[name]

    assert hasattr(from_, name), f'{from_!r} has no attribute "{name}"'

    return getattr(from_, name)


@cache
def is_typed_sequence(annotation: typing.Any) -> bool:
    origin = typing.get_origin(annotation)
    return origin and issubclass(origin, collections.abc.Sequence)


@cache
def is_typed_mapping(annotation: typing.Any) -> bool:
    origin = typing.get_origin(annotation)
    return origin and issubclass(origin, collections.abc.Mapping)


@cache
def get_item_type(annotation: typing.Any) -> typing.Any:
    args = typing.get_args(annotation)
    if is_typed_sequence(annotation):
        return args[0]

    if is_typed_mapping(annotation):
        return args[1]
