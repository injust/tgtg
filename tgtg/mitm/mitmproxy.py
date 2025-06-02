from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from anyio import create_task_group
from loguru import logger
from mitmproxy import optmanager
from mitmproxy.addons import default_addons, errorcheck, script
from mitmproxy.master import Master
from mitmproxy.options import Options

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable


@asynccontextmanager
async def mitmproxy(*, conf_dir: Path | None = None, scripts: Iterable[object] = ()) -> AsyncGenerator[Master]:
    if conf_dir is None:
        conf_dir = Path.cwd() / ".mitmproxy"

    master = Master(Options(confdir=str(conf_dir)), with_termlog=True)

    addons: list[object] = [addon for addon in default_addons() if not isinstance(addon, script.ScriptLoader)]  # type: ignore[no-untyped-call]
    addons.extend(scripts)  # Replace `script.ScriptLoader()` with `scripts`
    addons.append(errorcheck.ErrorCheck())  # Like `mitmproxy.tools.dump.DumpMaster`
    master.addons.add(*addons)  # type: ignore[no-untyped-call]  # pyright: ignore[reportUnknownMemberType]

    optmanager.load_paths(  # TODO(https://github.com/mitmproxy/mitmproxy/issues/7753)
        master.options, conf_dir / "config.yaml"
    )

    async with create_task_group() as tg:
        tg.start_soon(master.run)
        try:
            yield master
        finally:
            logger.debug("Shutting down")
            master.shutdown()  # type: ignore[no-untyped-call]
