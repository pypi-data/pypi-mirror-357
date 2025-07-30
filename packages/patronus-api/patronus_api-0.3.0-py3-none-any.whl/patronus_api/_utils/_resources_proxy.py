from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `patronus_api.resources` module.

    This is used so that we can lazily import `patronus_api.resources` only when
    needed *and* so that users can just import `patronus_api` and reference `patronus_api.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("patronus_api.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
