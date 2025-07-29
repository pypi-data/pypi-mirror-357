from kat_transform import schema, field, transform

import pytest


def test_transform():
    spec = schema("Schema", field(str, "field", transform=lambda x: x.lower()))

    raw = spec.get({"field": "UPPERCASE MESSAGE"})

    transformed = transform(raw)

    assert transformed == {"field": "uppercase message"}


def test_transform_subschema():
    sub = schema("Sub", field(str, "name", transform=lambda x: x.upper()))

    spec = schema("Schema", field(sub, "sub"))

    raw = spec.get({"sub": {"name": "name"}})

    transformed = transform(raw)

    assert transformed == {"sub": {"name": "NAME"}}


def test_transform_subschema_in_mutable_sequence():
    sub = schema("Sub", field(str, "name", transform=lambda x: x.upper()))

    spec = schema("Schema", field(list[sub], "sub"))

    raw = spec.get({"sub": [{"name": "name"}]})

    transformed = transform(raw)

    assert transformed == {"sub": [{"name": "NAME"}]}


def test_transform_subschema_in_immutable_sequence():
    sub = schema("Sub", field(str, "name", transform=lambda x: x.upper()))

    spec = schema("Schema", field(tuple[sub], "sub"))

    raw = spec.get({"sub": [{"name": "name"}]})

    transformed = transform(raw)

    assert transformed == {"sub": ({"name": "NAME"},)}


def test_transform_subschema_in_mapping():
    sub = schema("Sub", field(str, "name", transform=lambda x: x.upper()))

    spec = schema("Schema", field(dict[str, sub], "sub"))

    raw = spec.get({"sub": {"a": {"name": "name"}}})

    transformed = transform(raw)

    assert transformed == {"sub": {"a": {"name": "NAME"}}}


def test_transform_with_getter():
    spec = schema("Schema", field(str, "field", getter=lambda: "value"))

    raw = spec.get({})

    with pytest.raises(AssertionError):
        transform(raw)
