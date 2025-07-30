import typing
import collections.abc


from .schema import SchemaSpec
from .field import FieldSpec, I, O
from .exceptions import FieldResolveError
from .markers import ValueGetter, FieldValue
from .resolve_fields import resolve_fields, resolve_getter
from .util import get_item_type, is_typed_mapping, is_typed_sequence
from .metadata import CombinedMetadata, SchemaMetadata, FieldMetadata

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
    meta: FieldMetadata | CombinedMetadata[FieldMetadata] | None = None,
) -> FieldSpec[I, O]:
    """
    Shorthand for FieldSpec creation
    """
    return FieldSpec(type_, name, transform, getter, meta)


def schema(
    name: str,
    *fields: FieldSpec[typing.Any, typing.Any],
    meta: SchemaMetadata | CombinedMetadata[SchemaMetadata] | None = None,
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

    item_type = get_item_type(spec.output_type)
    if not isinstance(item_type, SchemaSpec):
        return value

    if is_typed_sequence(spec.output_type):
        assert isinstance(
            value, collections.abc.Sequence
        ), f"Expected sequence value, but got {type(value)}"
        sequence = typing.cast(tuple[frozenset[FieldValue]], value)
        return [transform(subraw) for subraw in sequence]

    elif is_typed_mapping(spec.output_type):
        assert isinstance(
            value, collections.abc.Mapping
        ), f"Expected mapping value, but got {type(value)}"
        mapping = typing.cast(collections.abc.Mapping[str, frozenset[FieldValue]], value)
        return {k: transform(vraw) for k, vraw in mapping.items()}

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
