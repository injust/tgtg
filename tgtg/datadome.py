from __future__ import annotations

from http import HTTPStatus
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, ClassVar, override

import httpx
from attrs import define, field
from loguru import logger
from packaging.version import Version
from whenever import Instant, TimeDelta, seconds

from ._client import ANDROID_VERSION, APP_VERSION, BUILD_ID, BUILD_NUMBER, HTTPX_LIMITS, USER_AGENT, BaseClient

if TYPE_CHECKING:
    from http.cookiejar import CookieJar

logger = logger.opt(colors=True)

COOKIE_NAME = "datadome"


@define(eq=False)
class DataDomeSdk(BaseClient):
    cookies: CookieJar
    last_sync: Instant = field(init=False, default=Instant.MIN)
    timestamps: list[Instant] = field(init=False, factory=list)

    SDK_VERSION: ClassVar[Version] = Version("3.0.0")
    SYNC_INTERVAL: ClassVar[TimeDelta] = seconds(10)

    @override
    def __attrs_post_init__(self) -> None:
        self.httpx = httpx.AsyncClient(
            headers={"Accept-Encoding": "gzip", "User-Agent": "okhttp/5.0.0-alpha.14"}, http2=True, limits=HTTPX_LIMITS
        )
        del self.httpx.headers["Accept"]  # TODO(https://github.com/encode/httpx/discussions/3037)

    async def on_response(self, response: httpx.Response) -> None:
        self.timestamps.append(now := Instant.now())
        if now - self.last_sync < self.SYNC_INTERVAL or not self.cookies:
            return

        cookie = next(cookie for cookie in self.cookies if cookie.name == COOKIE_NAME)
        self.last_sync = now
        timestamps = self.timestamps
        self.timestamps = []

        r = await self.httpx.post(
            "https://api-sdk.datadome.co/sdk/",
            data={
                "cid": cookie.value,
                "ddk": "1D42C2CA6131C526E09F294FE96F94",
                "request": response.request.url,
                "ua": USER_AGENT,
                "events": "["
                + ", ".join(
                    f'{{"id":1, "message":"response validation", "source":"sdk", "date":{ts.timestamp_millis()}}}'
                    for ts in timestamps
                )
                + "]",
                "inte": "android-java-okhttp",
                "ddv": self.SDK_VERSION,
                "ddvc": APP_VERSION,
                "os": "Android",
                "osr": ANDROID_VERSION,
                "osn": "VANILLA_ICE_CREAM",
                "osv": 36,
                "screen_x": 1080,
                "screen_y": 2400,
                "screen_d": 2.625,
                "camera": '{"auth":"false", "info":"{}"}',
                "mdl": "Pixel 6a",
                "prd": "bluejay",
                "mnf": "Google",
                "dev": "bluejay",
                "hrd": "bluejay",
                "fgp": f"google/bluejay/bluejay:{ANDROID_VERSION}/{BUILD_ID}/{BUILD_NUMBER}:user/release-keys",
                "tgs": "release-keys",
            },
        )
        r.status_code = HTTPStatus(r.status_code)

        data = r.json()
        match data["status"]:
            case HTTPStatus.OK:
                cookie.value = SimpleCookie(data["cookie"])[COOKIE_NAME].value
            case _:
                logger.error("{!r}<normal>: {}</normal>", r.status_code, data)


class CaptchaError(Exception):
    pass
