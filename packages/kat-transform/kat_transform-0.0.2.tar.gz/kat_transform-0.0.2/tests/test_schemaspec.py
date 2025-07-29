import typing
from kat_transform import FieldSpec, field, FieldMetadata, schema, SchemaMetadata, SchemaSpec

import pytest

from kat_transform.markers import FieldValue, ValueGetter


@pytest.fixture
def field_spec() -> FieldSpec[typing.Any, typing.Any]:
    return field(str, "field")


@pytest.fixture
def field_spec_getter() -> FieldSpec[typing.Any, typing.Any]:
    transform = lambda x: None
    getter = lambda from_object: None
    metadata = FieldMetadata()

    return field(str, "field", transform=transform, getter=getter, meta=metadata)


def test_schema_func_result(field_spec_getter):
    metadata = SchemaMetadata()

    func_result = schema("Schema", field_spec_getter, meta=metadata)

    assert func_result == SchemaSpec("Schema", (field_spec_getter,), metadata)


def test_get(field_spec):
    spec = schema("Schema", field_spec)

    raw = spec.get({"field": "value"})

    assert raw == {
        FieldValue(field_spec, "value"),
    }


def test_get_with_getter(field_spec_getter):
    spec = schema("Schema", field_spec_getter)

    raw = spec.get({})

    assert raw == {
        FieldValue(
            field_spec_getter,
            ValueGetter(field_spec_getter.getter, {}, field_spec_getter),
        ),
    }


def test_transform():
    spec = schema("Schema", field(str, "field", transform=lambda x: x.lower()))

    raw = spec.get({"field": "UPPERCASE MESSAGE"})

    transformed = spec.transform(raw)

    assert transformed == {"field": "uppercase message"}


def test_transform_with_getter(field_spec_getter):
    spec = schema("Schema", field_spec_getter)

    raw = spec.get({})

    with pytest.raises(AssertionError):
        spec.transform(raw)
