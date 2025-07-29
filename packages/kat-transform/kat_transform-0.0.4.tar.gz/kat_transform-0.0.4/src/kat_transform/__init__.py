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
    "transform",
    "SchemaSpec",
    "FieldValue",
    "ValueGetter",
    "FieldMetadata",
    "SchemaMetadata",
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


def transform_value(value: typing.Any, spec: FieldSpec[typing.Any, typing.Any]) -> typing.Any:
    if spec.transform is not None:
        value = spec.transform(value)

    if isinstance(spec.output_type, SchemaSpec):
        return transform(value)

    if not isinstance(spec.item_type, SchemaSpec):
        return value

    if spec.is_typed_mutable_sequence:
        sequence = typing.cast(tuple[frozenset[FieldValue]], value)
        return [transform(subraw) for subraw in sequence]

    elif spec.is_typed_sequence:
        sequence = typing.cast(tuple[frozenset[FieldValue]], value)
        return tuple(transform(subraw) for subraw in sequence)

    elif spec.is_typed_mapping:
        mapping = typing.cast(tuple[tuple[str, frozenset[FieldValue]]], value)
        return {k: transform(vraw) for k, vraw in mapping}

    else:
        raise RuntimeError("Unexpected behavior")


def transform(raw: collections.abc.Set[FieldValue]) -> collections.abc.Mapping[str, typing.Any]:
    """
    Transform input values of fields into final values using field's transformers
    """
    transformed: dict[str, typing.Any] = {}

    for field_value in raw:
        assert not isinstance(field_value.value, ValueGetter), (
            "ValueGetter objects are not permitted in transformation. "
            "They should be resolved using dependency injection"
        )

        transformed[field_value.field_spec.name] = transform_value(
            field_value.value, field_value.field_spec
        )

    return transformed
