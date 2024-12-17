from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from typing import Self, override

import httpx as httpx_
from anyio.abc import AsyncResource
from attrs import define, field
from httpx._config import DEFAULT_LIMITS
from packaging.version import Version

from .utils import httpx_remove_HTTPStatusError_info_suffix, httpx_response_jsonlib

ANDROID_VERSION = 16
APP_VERSION = Version("25.7.11")
BUILD_ID = "BP2A.250705.008"
BUILD_NUMBER = 13578956
USER_AGENT = f"TGTG/{APP_VERSION} Dalvik/2.1.0 (Linux; U; Android {ANDROID_VERSION}; Pixel 6a Build/{BUILD_ID})"

httpx_.Response.json = httpx_response_jsonlib  # type: ignore[method-assign]
httpx_.Response.raise_for_status = httpx_remove_HTTPStatusError_info_suffix(httpx_.Response.raise_for_status)  # type: ignore[assignment, method-assign]  # pyright: ignore[reportAttributeAccessIssue]

HTTPX_LIMITS = httpx_.Limits(
    max_connections=DEFAULT_LIMITS.max_connections,
    max_keepalive_connections=DEFAULT_LIMITS.max_keepalive_connections,
    keepalive_expiry=60,
)


@define(eq=False)
class BaseClient(AsyncResource, ABC):
    httpx: httpx_.AsyncClient = field(init=False)
    _exit_stack: AsyncExitStack = field(init=False)

    @abstractmethod
    def __attrs_post_init__(self) -> None:
        raise NotImplementedError

    @override
    async def __aenter__(self) -> Self:
        async with AsyncExitStack() as exit_stack:
            await exit_stack.enter_async_context(self.httpx)
            self._exit_stack = exit_stack.pop_all()
        return self

    @override
    async def aclose(self) -> None:
        await self._exit_stack.aclose()
