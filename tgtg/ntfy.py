from __future__ import annotations

from enum import IntEnum
from typing import override

import httpx
from attrs import define

from ._client import HTTPX_LIMITS, BaseClient


class Priority(IntEnum):
    MIN = 1
    LOW = 2
    DEFAULT = 3
    HIGH = 4
    MAX = 5
    URGENT = 5


@define(eq=False)
class NtfyClient(BaseClient):
    topic: str

    @override
    def __attrs_post_init__(self) -> None:
        self.httpx = httpx.AsyncClient(http2=True, limits=HTTPX_LIMITS, base_url="https://ntfy.sh/")

    async def publish(self, message: str, *, priority: Priority = Priority.DEFAULT, tag: str = "") -> None:
        headers: dict[str, str] = {}
        if priority != Priority.DEFAULT:
            headers["X-Priority"] = str(priority)
        if tag:
            headers["X-Tags"] = tag

        await self.httpx.post(self.topic, content=message, headers=headers)
