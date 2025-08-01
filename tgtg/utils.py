from __future__ import annotations

from functools import wraps
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, NamedTuple

import httpx
import humanize
import orjson as jsonlib
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from http.cookiejar import FileCookieJar

    import whenever
    from whenever import Date, Time, TimeDelta


# TODO(https://github.com/ariebovenberg/whenever/issues/37): Replace with whenever's interval type
class Interval[T: whenever._CommonISOMixin](NamedTuple):
    start: T
    end: T


def format_time(time: Time) -> str:
    return (
        time.py_time()
        .strftime(
            f"%I:%M:%S.{time.nanosecond // 1_000_000:03d} %p"
            if time.nanosecond > 999_999
            else "%I:%M:%S %p"
            if time.second
            else "%I:%M %p"
        )
        .removeprefix("0")
    )


def format_tz_offset(offset: TimeDelta) -> str:
    return "{:+03}:{:02}".format(*offset.in_hrs_mins_secs_nanos()) if offset else "Z"


def relative_date(date: Date) -> str:
    return humanize.naturalday(date.py_date()).replace(" 0", " ")


def relative_local_datetime(ts: whenever._ExactTime) -> tuple[str, str]:
    local_ts = ts.to_system_tz()
    return relative_date(local_ts.date()).capitalize(), format_time(local_ts.time())


def httpx_remove_HTTPStatusError_info_suffix(  # noqa: N802
    raise_for_status: Callable[[httpx.Response], httpx.Response],
) -> Callable[[httpx.Response], httpx.Response]:
    @wraps(raise_for_status)
    def wrapper(self: httpx.Response) -> httpx.Response:
        try:
            return raise_for_status(self)
        except httpx.HTTPStatusError as e:
            assert len(e.args) == 1 and isinstance(e.args[0], str), e.args
            message, removed = e.args[0].rsplit("\n", 1)
            assert removed.startswith("For more information check:"), removed
            e.args = (message,)
            raise

    return wrapper


def httpx_response_json_or_text(r: httpx.Response) -> object:
    try:
        return r.json()
    except JSONDecodeError:
        return r.text


# TODO(https://github.com/encode/httpx/issues/717)
@wraps(httpx.Response.json)
def httpx_response_jsonlib(self: httpx.Response, **kwargs: Any) -> Any:
    return jsonlib.loads(self.content, **kwargs)


def load_cookie_jar(cookie_jar: FileCookieJar) -> FileCookieJar:
    try:
        cookie_jar.load()
    except FileNotFoundError as e:
        logger.debug(e)
        logger.warning("Could not load cookies from {!r}, using an empty CookieJar", cookie_jar.filename)

    return cookie_jar
