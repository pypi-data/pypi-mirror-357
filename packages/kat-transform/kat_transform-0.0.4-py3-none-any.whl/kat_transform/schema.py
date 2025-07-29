import typing
import collections.abc
from dataclasses import dataclass

from .field import FieldSpec
from .markers import FieldValue
from .metadata import SchemaMetadata


def get_by_item(
    item_type: "SchemaSpec",
    value: collections.abc.Mapping[str, typing.Any] | collections.abc.Sequence[typing.Any],
    spec: FieldSpec[typing.Any, typing.Any],
) -> FieldValue:
    if spec.is_typed_mapping:
        mapping = typing.cast(collections.abc.Mapping[str, typing.Any], value)

        mapping_schema_fields = tuple(
            (key, frozenset(item_type.get(item))) for key, item in mapping.items()
        )
        return FieldValue(spec, mapping_schema_fields)

    elif spec.is_typed_sequence:
        array = typing.cast(collections.abc.Sequence[typing.Any], value)

        array_schema_fields = [frozenset(item_type.get(item)) for item in array]
        return FieldValue(spec, array_schema_fields)
    else:
        raise RuntimeError("Unexpected behavior")


@dataclass(frozen=True)
class SchemaSpec:
    """
    Schema used to transform python objects into mappings. Should be used to transform data before serialization
    """

    name: str
    fields: collections.abc.Sequence[FieldSpec[typing.Any, typing.Any]]
    metadata: SchemaMetadata | None = None

    def get(self, from_: typing.Any) -> set[FieldValue]:
        """
        Get input values of fields
        """
        fields: set[FieldValue] = set()

        for spec in self.fields:
            field_value = spec.get(from_)

            if isinstance(spec.output_type, SchemaSpec):
                sub_schema_fields = spec.output_type.get(field_value)
                fields.add(FieldValue(spec, frozenset(sub_schema_fields)))
                continue

            elif isinstance(spec.item_type, SchemaSpec):
                fields.add(get_by_item(spec.item_type, typing.cast(typing.Any, field_value), spec))
                continue

            fields.add(FieldValue(spec, field_value))

        return fields

    def __hash__(self) -> int:
        return hash((self.name,) + tuple(self.fields))
