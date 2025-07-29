import typing
import collections.abc
from dataclasses import dataclass

from .field import FieldSpec
from .metadata import SchemaMetadata
from .markers import ValueGetter, FieldValue


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

    def transform(
        self, values: collections.abc.Set[FieldValue]
    ) -> collections.abc.Mapping[str, typing.Any]:
        """
        Transform input values of fields into final values using field's transformers
        """
        transformed: dict[str, typing.Any] = {}

        for field_value in values:
            assert not isinstance(field_value.value, ValueGetter), (
                "ValueGetter objects are not permitted in transformation. "
                "They should be resolved using dependency injection"
            )

            value = field_value.value
            spec = field_value.field_spec

            if isinstance(spec.output_type, SchemaSpec):
                value = spec.output_type.transform(value)
            elif spec.transform is not None:
                value = spec.transform(field_value.value)

            transformed[spec.name] = value

        return transformed

    def __hash__(self) -> int:
        return hash((self.name,) + tuple(self.fields))
