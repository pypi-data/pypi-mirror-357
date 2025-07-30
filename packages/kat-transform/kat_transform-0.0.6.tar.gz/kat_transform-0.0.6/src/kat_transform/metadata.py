import typing

T = typing.TypeVar("T", bound="Metadata")
T_co = typing.TypeVar("T_co", bound="Metadata", covariant=True)


class Metadata:
    @property
    def entries(self: T_co) -> tuple[T_co, ...]:
        return (self,)

    def get_metadata(self, metadata_type: type[T], exact: bool = False) -> T | None:
        for entry in self.entries:
            if type(entry) is metadata_type:
                return entry

            if not exact and isinstance(entry, metadata_type):
                return entry

        return None

    def __or__(self: T_co, other: T_co) -> "CombinedMetadata[T_co]":
        return CombinedMetadata[T_co](*self.entries, *other.entries)


class CombinedMetadata(Metadata, typing.Generic[T_co]):
    def __init__(self, *entries: T_co):
        self._entries: tuple[T_co, ...] = entries

    @property
    def entries(self) -> tuple[T_co, ...]:
        return self._entries


class FieldMetadata(Metadata):
    """
    Field metadata that can be used by other tools (like json schema generation)

    This is fully customisable and up to you, how to and for what use it
    """


class SchemaMetadata(Metadata):
    """
    Schema metadata that can be used by other tools (like json schema generation)

    This is fully customisable and up to you, how to and for what use it
    """
