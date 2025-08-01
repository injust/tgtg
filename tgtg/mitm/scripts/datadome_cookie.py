from __future__ import annotations

from http import HTTPStatus
from http.cookiejar import Cookie, FileCookieJar, MozillaCookieJar
from http.cookies import SimpleCookie
from pathlib import Path
from typing import TYPE_CHECKING

import orjson as jsonlib
from loguru import logger

if TYPE_CHECKING:
    from mitmproxy.http import HTTPFlow

logger = logger.opt(colors=True)

COOKIE_NAME = "datadome"
COOKIES_PATH = Path.cwd() / "cookies.txt"


class DataDomeCookie:
    cookies: FileCookieJar

    def __init__(self, cookies: FileCookieJar | None = None) -> None:
        if cookies is None:
            self.cookies = MozillaCookieJar(COOKIES_PATH)
            self.cookies.load()
        else:
            self.cookies = cookies

    @property
    def cookie(self) -> Cookie:
        return next(cookie for cookie in self.cookies if cookie.name == COOKIE_NAME)

    async def response(self, flow: HTTPFlow) -> None:
        if flow.request.pretty_host == "api-sdk.datadome.co" and flow.response:
            flow.response.status_code = HTTPStatus(flow.response.status_code)

            if flow.response.status_code == HTTPStatus.OK and flow.response.content:
                data = jsonlib.loads(flow.response.content)
                match data["status"]:
                    case HTTPStatus.OK:
                        cookie = self.cookie
                        cookie.value = SimpleCookie(data["cookie"])[COOKIE_NAME].value
                        logger.debug(cookie.value)
                        self.cookies.save(str(COOKIES_PATH))
                    case _:
                        logger.error("{!r}<normal>: {}</normal>", flow.response.status_code, data)


if __name__.startswith("__mitmproxy_script__."):
    addons = [DataDomeCookie()]
