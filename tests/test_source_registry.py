import pytest

from reachkit.core.errors import InputError
from reachkit.core.models import SourceResult
from reachkit.sources.registry import SourceRegistry, default_registry


class Reader:
    name = "sample"

    def read(self, **kwargs):
        return SourceResult(source="sample", url=None, title=None, content_type=None, items=[])


def test_registry_returns_registered_reader():
    registry = SourceRegistry()
    reader = Reader()

    registry.register(reader)

    assert registry.get("sample") is reader


def test_registry_rejects_unknown_reader():
    registry = SourceRegistry()

    with pytest.raises(InputError):
        registry.get("missing")


def test_registry_lists_names_in_registration_order():
    registry = SourceRegistry()
    registry.register(Reader())

    assert registry.names() == ["sample"]


def test_default_registry_is_initially_empty_for_foundation_layer():
    assert default_registry().names() == []
