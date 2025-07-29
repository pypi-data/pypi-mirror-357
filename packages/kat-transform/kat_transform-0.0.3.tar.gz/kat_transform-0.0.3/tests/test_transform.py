from kat_transform import schema, field, transform

import pytest


def test_transform():
    spec = schema("Schema", field(str, "field", transform=lambda x: x.lower()))

    raw = spec.get({"field": "UPPERCASE MESSAGE"})

    transformed = transform(raw)

    assert transformed == {"field": "uppercase message"}


def test_transform_with_getter():
    spec = schema("Schema", field(str, "field", getter=lambda: "value"))

    raw = spec.get({})

    with pytest.raises(AssertionError):
        transform(raw)
