"""Custom type annotations."""

from __future__ import annotations

from collections.abc import MutableMapping

JSON = MutableMapping[str, bool | int | str | list[str]]
"""A JSON-serialisable object."""

PARAMS = MutableMapping[str, int | str]
"""URL query parameters."""
