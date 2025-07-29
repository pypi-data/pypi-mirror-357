import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .field import FieldSpec


@dataclass(frozen=True)
class ValueGetter:
    """
    Marker for upstream transformation logic, that field value needs to be resolved using dependency injection
    """

    callable: typing.Callable[..., typing.Any]
    """
    Callable on which dependency injection should be called
    """

    from_object: typing.Any
    """
    Object that should be passed as "from_object" into dependency injection scope
    """

    field_spec: "FieldSpec[typing.Any, typing.Any]"
    """
    Field spec this getter came from. Can be used for debugging purposes
    """

    def __hash__(self) -> int:
        return hash(self.field_spec)


@dataclass(frozen=True)
class FieldValue:
    """
    Marker that holds field's value with a pointer to it's spec
    """

    field_spec: "FieldSpec[typing.Any, typing.Any]"
    value: typing.Any | ValueGetter

    def __hash__(self) -> int:
        return hash(self.field_spec)
