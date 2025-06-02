from __future__ import annotations

from asyncio import CancelledError
from contextlib import suppress

import anyio

from . import mitmproxy
from .scripts import DataDomeCookie


async def main() -> None:
    with suppress(CancelledError):
        async with mitmproxy(scripts=[DataDomeCookie()]) as master:
            await master.should_exit.wait()


if __name__ == "__main__":
    anyio.run(main)
