from __future__ import annotations

import asyncio
import os
import site
import sys
import threading
import warnings
from _colorize import get_theme
from asyncio import Task
from asyncio.__main__ import AsyncIOInteractiveConsole  # pyright: ignore[reportMissingTypeStubs]
from platform import python_version
from textwrap import dedent
from typing import TYPE_CHECKING, Any, override

from ._client import APP_VERSION

if TYPE_CHECKING:
    from types import ModuleType


class REPLThread(threading.Thread):
    @override
    def run(self) -> None:
        global return_code

        try:
            banner = f"""
                TGTG {APP_VERSION} REPL on Python {python_version()}
                Use "await" directly instead of "asyncio.run()".

            """
            console.write(dedent(banner.strip("\n")))

            if startup_path := os.getenv("PYTHONSTARTUP"):
                sys.audit("cpython.run_startup", startup_path)

                import tokenize  # noqa: PLC0415

                with tokenize.open(startup_path) as f:
                    startup_code = compile(f.read(), startup_path, "exec")
                    exec(startup_code, console.locals)

            ps1 = getattr(sys, "ps1", ">>> ")
            if CAN_USE_PYREPL:
                theme = get_theme().syntax
                ps1 = f"{theme.prompt}{ps1}{theme.reset}"

            commands = """
                from tgtg._repl import make_client
                client = await make_client()
                from inspect import getmembers, ismethod
                locals().update((name, func) for name, func in getmembers(client, ismethod) if not name.startswith("_"))
            """
            for command in dedent(commands.strip("\n")).splitlines():
                console.write(f"{ps1}{command}\n")
                console.runsource(command)

            if CAN_USE_PYREPL:
                from _pyrepl.simple_interact import (  # pyright: ignore[reportMissingTypeStubs]  # noqa: PLC0415
                    run_multiline_interactive_console,
                )

                try:
                    run_multiline_interactive_console(console)
                except SystemExit:
                    # expected via the `exit` and `quit` commands
                    pass
                except BaseException:
                    # unexpected issue
                    console.showtraceback()
                    console.write("Internal error, ")
                    return_code = 1
            else:
                console.interact(banner="", exitmsg="")
        finally:
            warnings.filterwarnings("ignore", message=r"^coroutine .* was never awaited$", category=RuntimeWarning)

            loop.call_soon_threadsafe(loop.stop)

    def interrupt(self) -> None:
        if not CAN_USE_PYREPL:
            return

        from _pyrepl.simple_interact import _get_reader  # pyright: ignore[reportMissingTypeStubs]  # noqa: PLC0415

        r = _get_reader()
        if r.threading_hook is not None:
            r.threading_hook.add("")  # pyright: ignore[reportFunctionMemberAccess]


if __name__ == "__main__":
    sys.audit("cpython.run_stdin")

    if os.getenv("PYTHON_BASIC_REPL"):
        CAN_USE_PYREPL = False  # pyright: ignore[reportConstantRedefinition]
    else:
        from _pyrepl.main import (  # type: ignore[no-redef]  # pyright: ignore[reportMissingTypeStubs]
            CAN_USE_PYREPL,  # pyright: ignore[reportConstantRedefinition]
        )

    return_code: sys._ExitCode = 0
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    repl_locals: dict[str, object] = {}
    for key in "__name__", "__package__", "__loader__", "__spec__", "__builtins__", "__file__":
        repl_locals[key] = locals()[key]

    console = AsyncIOInteractiveConsole(repl_locals, loop)

    repl_future: Task[Any] | None = None
    keyboard_interrupted = False

    readline: ModuleType | None
    try:
        import readline
    except ImportError:
        readline = None

    interactive_hook = getattr(sys, "__interactivehook__", None)

    if interactive_hook is not None:
        sys.audit("cpython.run_interactivehook", interactive_hook)
        interactive_hook()

    if interactive_hook is site.register_readline:
        # Fix the completer function to use the interactive console locals
        try:
            import rlcompleter
        except ImportError:
            pass
        else:
            if readline is not None:
                completer = rlcompleter.Completer(console.locals)
                readline.set_completer(completer.complete)

    repl_thread = REPLThread(name="Interactive thread")
    repl_thread.daemon = True
    repl_thread.start()

    while True:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            keyboard_interrupted = True
            if repl_future and not repl_future.done():
                repl_future.cancel()  # pyright: ignore[reportUnreachable]
            repl_thread.interrupt()
            continue
        else:
            break

    console.write("exiting TGTG REPL...\n")
    sys.exit(return_code)
