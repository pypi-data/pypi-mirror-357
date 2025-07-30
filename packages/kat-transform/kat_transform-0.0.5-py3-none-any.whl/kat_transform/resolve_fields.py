import typing
import collections.abc
from contextlib import ExitStack

from .schema import SchemaSpec
from .exceptions import FieldResolveError
from .markers import ValueGetter, FieldValue

from fundi import scan, inject


def resolve_getter(
    scope: collections.abc.Mapping[str, typing.Any], getter: ValueGetter
) -> typing.Any:
    """
    Resolve ValueGetter using dependency injection

    Asynchronous getters are prohibited!
    """
    with ExitStack() as stack:
        try:
            value = inject(
                {**scope, "from_object": getter.from_object}, scan(getter.callable), stack
            )
        except Exception as exc:
            raise FieldResolveError(getter.field_spec, getter.from_object)

    return value


def resolve_fields(
    scope: collections.abc.Mapping[str, typing.Any], raw: set[FieldValue]
) -> set[FieldValue]:
    """
    Resolve fields that define getters using dependency injection

    Asynchronous getters are prohibited!
    """
    values: set[FieldValue] = set()

    for field_value in raw:
        spec = field_value.field_spec
        value = field_value.value

        if isinstance(spec.output_type, SchemaSpec):
            assert isinstance(
                value, collections.abc.Set
            ), f"Expected field value to be set, but {type(value)} found"

            sub_values = resolve_fields(scope, typing.cast(set[FieldValue], value))

            values.add(FieldValue(spec, frozenset(sub_values)))
            continue

        if not isinstance(value, ValueGetter):
            values.add(field_value)
            continue

        values.add(FieldValue(spec, resolve_getter(scope, value)))

    return values
