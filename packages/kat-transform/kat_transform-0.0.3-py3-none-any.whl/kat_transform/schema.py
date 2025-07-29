import typing
import collections.abc
from dataclasses import dataclass

from .field import FieldSpec
from .markers import FieldValue
from .metadata import SchemaMetadata


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

            fields.add(FieldValue(spec, field_value))

        return fields

    def __hash__(self) -> int:
        return hash((self.name,) + tuple(self.fields))
