from kat_transform import FieldSpec, field, FieldMetadata

import pytest

from kat_transform.markers import ValueGetter


def test_field_func_result():
    transform = lambda x: None
    getter = lambda from_object: None
    metadata = FieldMetadata()

    func_result = field(str, "field", transform=transform, getter=getter, meta=metadata)

    assert func_result == FieldSpec(str, "field", transform, getter, metadata)


def test_get_by_field_name():
    spec = field(str, "field")

    class storage:
        field = "value"

    assert spec.get(storage) == "value"
    assert spec.get({"field": "value"}) == "value"

    with pytest.raises(AssertionError):
        spec.get({})


def test_get_by_single_getter():
    spec = field(str, "field", getter="alias")

    class storage:
        alias = "value"

    assert spec.get(storage) == "value"
    assert spec.get({"alias": "value"}) == "value"

    with pytest.raises(AssertionError):
        spec.get({})

    with pytest.raises(AssertionError):
        spec.get({"field": "value"})


def test_get_by_sequence_getter():
    spec = field(str, "field", getter=("alias", "field"))

    class storage:
        alias = "value"

    assert spec.get(storage) == "value"

    class storage:
        field = "value"

    assert spec.get(storage) == "value"

    assert spec.get({"alias": "value"}) == "value"
    assert spec.get({"field": "value"}) == "value"

    with pytest.raises(AssertionError):
        spec.get({})


def test_get_by_callable_getter():
    spec = field(str, "field", getter=lambda: "Field value")

    assert spec.get({}) == ValueGetter(spec.getter, {}, spec)
