import typing
import collections.abc

from .schema import SchemaSpec
from .field import FieldSpec, I, O
from .exceptions import FieldResolveError
from .markers import ValueGetter, FieldValue
from .metadata import SchemaMetadata, FieldMetadata
from .resolve_fields import resolve_fields, resolve_getter

__all__ = [
    "field",
    "schema",
    "FieldSpec",
    "FieldValue",
    "ValueGetter",
    "FieldMetadata",
    "resolve_getter",
    "resolve_fields",
    "FieldResolveError",
]


def field(
    type_: type[O] | SchemaSpec,
    name: str,
    transform: typing.Callable[[I], O] | None = None,
    getter: str | collections.abc.Sequence[str] | typing.Callable[..., I | O] | None = None,
    meta: FieldMetadata | None = None,
) -> FieldSpec[I, O]:
    """
    Shorthand for FieldSpec creation
    """
    return FieldSpec(type_, name, transform, getter, meta)


def schema(
    name: str, *fields: FieldSpec[typing.Any, typing.Any], meta: SchemaMetadata | None = None
) -> SchemaSpec:
    """
    Shorthand for SchemaSpec creation
    """
    return SchemaSpec(name, fields, meta)
