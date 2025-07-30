import typing

import pytest

from kat_transform import (
    field,
    schema,
    FieldSpec,
    SchemaSpec,
    FieldValue,
    ValueGetter,
    FieldMetadata,
    SchemaMetadata,
)


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
