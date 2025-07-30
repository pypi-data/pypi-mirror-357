import typing

from .field import FieldSpec


class FieldResolveError(Exception):
    """
    Could not resolve field
    """

    def __init__(self, spec: FieldSpec[typing.Any, typing.Any], from_object: typing.Any) -> None:
        message = f'Could not resolve value for "{spec.name}" field using getter {spec.getter} from {from_object!r}'
        super().__init__(message)
        self.field_spec: FieldSpec[typing.Any, typing.Any] = spec
        self.from_object: typing.Any = from_object
