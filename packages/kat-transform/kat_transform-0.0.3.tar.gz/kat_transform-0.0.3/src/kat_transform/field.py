import typing
import collections.abc
from dataclasses import dataclass


from .util import get_by_name
from .markers import ValueGetter
from .metadata import FieldMetadata

if typing.TYPE_CHECKING:
    from .schema import SchemaSpec

I = typing.TypeVar("I")
O = typing.TypeVar("O")


@dataclass(frozen=True)
class FieldSpec(typing.Generic[I, O]):
    """
    Field used to determine from where get value and how to transform it into serializable type
    """

    output_type: "type[O] | SchemaSpec"
    name: str

    transform: typing.Callable[[I], O] | None = None
    """
    Define transform callable that will be used to transform input value for this field before serialization
    """

    getter: str | collections.abc.Sequence[str] | typing.Callable[..., I | O] | None = None
    """
    Define name, list of names or callable that will be used to get input value for this field
    """

    metadata: FieldMetadata | None = None
    """
    Define metadata for this field
    """

    def get(self, from_: typing.Any) -> I | O | ValueGetter:
        """
        Get field input value from object

        If field's getter is a callable - returns special marker object,
        that should be used to resolve actual value using `resolve_fields` function
        """
        if callable(self.getter):
            return ValueGetter(self.getter, from_, self)

        if isinstance(self.getter, str):
            return get_by_name(self.getter, from_)

        if isinstance(self.getter, collections.abc.Sequence):
            for name in self.getter:
                try:
                    return get_by_name(name, from_)
                except AssertionError:
                    pass
            else:
                assert (
                    False
                ), f'No value was found for sequence of names: "{self.getter!r}" in {from_!r}'

        return get_by_name(self.name, from_)

    def __hash__(self) -> int:
        return hash(self.name)
