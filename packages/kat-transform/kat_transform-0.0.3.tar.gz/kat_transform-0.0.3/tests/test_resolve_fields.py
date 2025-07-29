import secrets
from fundi import from_
from kat_transform import field, resolve_fields, schema


def test_default():
    field_spec = field(str, "field", getter=lambda from_object: from_object["object_value"])
    spec = schema("Schema", field_spec)

    raw = spec.get({"object_value": "Field value"})

    resolved = resolve_fields({}, raw)

    field_value = resolved.pop()

    assert field_value.value == "Field value"
    assert field_value.field_spec == field_spec


def test_with_dependencies():
    def dependency():
        return "Declarative is easier than imperative"

    def getter(x: str = from_(dependency)):
        return hash(x)

    field_spec = field(int, "field", getter=getter)

    spec = schema("Schema", field_spec)

    raw = spec.get({})

    resolved = resolve_fields({}, raw)

    field_value = resolved.pop()

    assert field_value.value == hash("Declarative is easier than imperative")
    assert field_value.field_spec == field_spec


def test_with_scope():
    field_spec = field(str, "field", getter=lambda scope_value: scope_value.lower())

    spec = schema("Schema", field_spec)

    raw = spec.get({})

    resolved = resolve_fields({"scope_value": "UPPERCASE MESSAGE"}, raw)

    field_value = resolved.pop()

    assert field_value.value == "uppercase message"
    assert field_value.field_spec == field_spec
