from kat_transform.metadata import Metadata


def test_combination():
    class CustomMeta(Metadata): ...

    custom = CustomMeta()
    empty = Metadata()

    combined = custom | empty
    assert combined.entries == (custom, empty)

    assert combined.get_metadata(CustomMeta) is custom

    assert combined.get_metadata(Metadata) is custom
    assert combined.get_metadata(Metadata, exact=True) is empty
