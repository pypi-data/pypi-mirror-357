import secrets
from fundi import from_
from kat_transform import field, ValueGetter, resolve_getter


def test_default():
    spec = field(str, "field", getter=lambda from_object: from_object["object_value"])

    getter = spec.get({"object_value": "Field value"})

    assert isinstance(getter, ValueGetter)

    resolved = resolve_getter({}, getter)

    assert resolved == "Field value"


def test_with_dependencies():
    def dependency():
        return "Declarative is easier than imperative"

    def getter(x: str = from_(dependency)):
        return hash(x)

    spec = field(int, "field", getter=getter)

    getter = spec.get({})

    assert isinstance(getter, ValueGetter)

    assert resolve_getter({}, getter) == hash("Declarative is easier than imperative")


def test_with_scope():
    spec = field(str, "field", getter=lambda scope_value: scope_value.lower())

    getter = spec.get({})

    assert isinstance(getter, ValueGetter)

    assert resolve_getter({"scope_value": "UPPERCASE MESSAGE"}, getter) == "uppercase message"
