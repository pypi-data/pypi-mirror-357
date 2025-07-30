import typing
import collections.abc
from dataclasses import dataclass


from .field import FieldSpec
from .markers import FieldValue
from .metadata import CombinedMetadata, SchemaMetadata
from .util import get_item_type, is_typed_mapping, is_typed_sequence


def get_by_item(
    item_type: "SchemaSpec",
    value: collections.abc.Mapping[str, typing.Any] | collections.abc.Sequence[typing.Any],
    spec: FieldSpec[typing.Any, typing.Any],
) -> FieldValue:
    if is_typed_mapping(spec.output_type):
        mapping = typing.cast(collections.abc.Mapping[str, typing.Any], value)

        mapping_schema_fields = {key: item_type.get(item) for key, item in mapping.items()}
        return FieldValue(spec, mapping_schema_fields)

    elif is_typed_sequence(spec.output_type):
        array = typing.cast(collections.abc.Sequence[typing.Any], value)

        array_schema_fields = [item_type.get(item) for item in array]
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
    metadata: SchemaMetadata | CombinedMetadata[SchemaMetadata] | None = None

    def get(self, from_: typing.Any) -> frozenset[FieldValue]:
        """
        Get input values of fields
        """
        fields: set[FieldValue] = set()

        for spec in self.fields:
            field_value = spec.get(from_)

            if isinstance(spec.output_type, SchemaSpec):
                sub_schema_fields = spec.output_type.get(field_value)
                fields.add(FieldValue(spec, sub_schema_fields))
                continue

            elif isinstance(item_type := get_item_type(spec.output_type), SchemaSpec):
                fields.add(get_by_item(item_type, typing.cast(typing.Any, field_value), spec))
                continue

            fields.add(FieldValue(spec, field_value))

        return frozenset(fields)

    def __hash__(self) -> int:
        return hash((self.name,) + tuple(self.fields))
