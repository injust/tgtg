from __future__ import annotations

from contextlib import AsyncExitStack
from http import HTTPStatus
from itertools import accumulate, count
from json import JSONDecodeError
from typing import TYPE_CHECKING, ClassVar, Self, cast, overload, override
from uuid import UUID, uuid4

import anyio
import httpx
import humanize
import orjson as jsonlib
from anyio import create_task_group
from apscheduler import AsyncScheduler
from attrs import Factory, asdict, define, field
from babel.core import default_locale
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt
from whenever import Instant, SystemDateTime, minutes, seconds

from ._client import APP_VERSION, HTTPX_LIMITS, USER_AGENT, BaseClient
from .api import TGTG_BASE_URL, TgtgApi
from .datadome import CaptchaError, DataDomeSdk
from .exceptions import (
    TgtgAlreadyAbortedError,
    TgtgApiError,
    TgtgCancelDeadlineError,
    TgtgEmailChangeError,
    TgtgItemDeletedError,
    TgtgItemDisabledError,
    TgtgLimitExceededError,
    TgtgLoginError,
    TgtgPaymentError,
    TgtgReservationBlockedError,
    TgtgSaleClosedError,
    TgtgSoldOutError,
    TgtgUnauthorizedError,
    TgtgValidationError,
)
from .models import Credentials, Favorite, Item, MultiUseVoucher, Payment, Reservation, Voucher
from .ntfy import NtfyClient, Priority
from .utils import format_tz_offset, httpx_response_json_or_text, load_cookie_jar

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable
    from http.cookiejar import FileCookieJar

    from .models import JSON

logger = logger.opt(colors=True)

NTFY_TOPIC = "tgtg-injust"


@define(eq=False)
class TgtgClient(BaseClient):
    cookies: FileCookieJar = field(converter=load_cookie_jar)
    credentials: Credentials = field(init=False)
    email: str = field(init=False)
    user_id: int = field(init=False, converter=int)

    correlation_id: UUID = field(init=False, factory=uuid4)
    device_id: UUID = field(init=False, factory=uuid4)

    datadome: DataDomeSdk = field(
        init=False, default=Factory(lambda self: DataDomeSdk(cast("TgtgClient", self).cookies), takes_self=True)
    )
    ntfy: NtfyClient = field(init=False, factory=lambda: NtfyClient(NTFY_TOPIC))
    scheduler: AsyncScheduler = field(init=False, factory=AsyncScheduler)  # pyright: ignore[reportArgumentType, reportCallIssue, reportUnknownVariableType]

    DEVICE_TYPE: ClassVar[str] = "ANDROID"
    LANGUAGE: ClassVar[str] = (default_locale() or "en_US").replace("_", "-")
    # Scarborough, Toronto, Canada
    LOCATION: ClassVar[dict[str, float]] = {"latitude": 43.7729744, "longitude": -79.2576479}
    # NOTE: This is actually a float on the wire, but the app constrains it to integer values
    RADIUS: ClassVar[int] = 30
    assert 0 < RADIUS <= 30

    @classmethod
    def from_credentials(cls, credentials: Credentials, cookies: FileCookieJar) -> Self:
        client = cls(cookies)
        client.credentials = credentials
        return client

    @classmethod
    def from_email(cls, email: str, cookies: FileCookieJar) -> Self:
        client = cls(cookies)
        client.email = email
        return client

    @override
    def __attrs_post_init__(self) -> None:
        self.httpx = httpx.AsyncClient(
            headers={
                "Accept-Encoding": "gzip",
                "Accept-Language": self.LANGUAGE,
                "User-Agent": USER_AGENT,
                "X-Correlation-ID": str(self.correlation_id),
            },
            cookies=self.cookies,
            http2=True,
            timeout=httpx.Timeout(5, read=2),  # Fail faster if server randomly drops the request
            limits=HTTPX_LIMITS,
            event_hooks={"response": [self.datadome.on_response]},
            base_url=TGTG_BASE_URL,
        )
        assert self.cookies is self.httpx.cookies.jar
        del self.httpx.headers["Accept"]  # TODO(https://github.com/encode/httpx/discussions/3037)

        logger.debug("TGTG app version<normal>: {}</normal>", APP_VERSION)
        logger.debug("User agent<normal>: {}</normal>", USER_AGENT)

    @override
    async def __aenter__(self) -> Self:
        async with AsyncExitStack() as exit_stack:
            await exit_stack.enter_async_context(self.httpx)
            await exit_stack.enter_async_context(self.datadome)
            await exit_stack.enter_async_context(self.ntfy)

            if not hasattr(self, "credentials"):
                self.credentials = await self.login(self.email)

            startup_data = await self.get_startup_data()
            self.email = startup_data["user"]["email"]
            self.user_id = startup_data["user"]["user_id"]
            logger.debug("Email<normal>: {}</normal>", self.email)

            tg = await exit_stack.enter_async_context(create_task_group())
            tg.start_soon(self._check_user_profile)

            await exit_stack.enter_async_context(self.scheduler)
            await tg.start(self.scheduler.run_until_stopped)
            self._exit_stack = exit_stack.pop_all()
        return self

    @retry(
        stop=stop_after_attempt(2),
        retry=retry_if_exception_type(
            (
                httpx.ReadTimeout,  # Server sporadically drops requests without processing them, should be safe to retry
                httpx.RemoteProtocolError,  # https://github.com/encode/httpx/discussions/3549
            )
        ),
        reraise=True,
    )
    async def _post(self, endpoint: TgtgApi, *path_params: str | int, json: JSON | None = None) -> JSON:
        if endpoint.includes_credentials and endpoint != TgtgApi.TOKEN_REFRESH:
            await self.refresh_credentials()

        headers = {"Content-Type": f"application/json{'' if json is None else '; charset=utf-8'}"}
        if endpoint in {TgtgApi.FAVORITES, TgtgApi.ITEMS, TgtgApi.ITEM_STATUS}:
            headers["X-24HourFormat"] = "false"
            headers["X-TimezoneOffset"] = format_tz_offset(SystemDateTime.now().offset)
        r = await self.httpx.post(
            endpoint.format(*path_params),
            content=None if json is None else jsonlib.dumps(json),
            headers=headers,
            auth=self.credentials if endpoint.includes_credentials else httpx.USE_CLIENT_DEFAULT,
        )
        r.status_code = HTTPStatus(r.status_code)

        match r.status_code, endpoint:
            case HTTPStatus.BAD_REQUEST, TgtgApi.USER_EMAIL_CHANGE if r.json() == {
                "errors": [{"code": "INVALID_EMAIL_CHANGE_REQUEST"}]
            }:
                raise TgtgEmailChangeError
            case HTTPStatus.BAD_REQUEST, TgtgApi.ITEM_STATUS if r.json() == {"errors": [{"code": "VALIDATION_ERROR"}]}:
                raise TgtgValidationError
            case HTTPStatus.UNAUTHORIZED, _ if endpoint.includes_credentials and endpoint != TgtgApi.TOKEN_REFRESH:
                logger.warning("{!r}<normal>: {}</normal>", r.status_code, httpx_response_json_or_text(r))

                try:
                    await self.refresh_credentials(force=True)
                except TgtgApiError as e:
                    raise ValueError("Invalid credentials") from e
                else:
                    return await self._post(endpoint, *path_params, json=json)
            case HTTPStatus.FORBIDDEN, _ if "X-DD-B" in r.headers:
                # TODO: Handle DataDome CAPTCHA
                logger.opt(colors=False).debug(r.text)
                await self.ntfy.publish("DataDome CAPTCHA", priority=Priority.HIGH, tag="rotating_light")
                await self.scheduler.stop()
                raise CaptchaError
            case HTTPStatus.FORBIDDEN, _ if r.json() == {"errors": [{"code": "UNAUTHORIZED"}]}:
                raise TgtgUnauthorizedError
            case HTTPStatus.GONE, TgtgApi.ITEM_STATUS if r.json() == {"errors": [{"code": "ENTITY_DELETED"}]}:
                raise TgtgItemDeletedError
            case HTTPStatus.GONE, TgtgApi.ITEM_STATUS if r.json() == {"errors": [{"code": "ENTITY_DISABLED"}]}:
                raise TgtgItemDisabledError
            case HTTPStatus.ACCEPTED, TgtgApi.AUTH_BY_POLLING if not r.content:
                return {}
            case (
                HTTPStatus.OK,
                TgtgApi.USER_DATA_EXPORT
                | TgtgApi.USER_DELETE
                | TgtgApi.USER_EMAIL_CHANGE
                | TgtgApi.USER_SET_DEVICE
                | TgtgApi.AUTH_LOGOUT
                | TgtgApi.ITEM_FAVORITE,
            ) if not r.content:
                return {}
            case HTTPStatus.OK, _:
                pass
            case _:
                logger.error("{!r}<normal>: {}</normal>", r.status_code, httpx_response_json_or_text(r))
                r.raise_for_status()

        try:
            data: JSON = r.json()
        except JSONDecodeError as e:
            raise ValueError("Could not decode response as JSON", r.text) from e
        else:
            return data

    async def login(self, email: str) -> Credentials:
        data = await self._post(TgtgApi.AUTH_BY_EMAIL, json={"device_type": self.DEVICE_TYPE, "email": email})

        match data["state"]:
            case "TERMS":
                raise TgtgLoginError(f"{email} is not linked to a TGTG account (hint: sign up in the app first)")
            case "WAIT":
                return await self.poll_login(email, data["polling_id"])
            case _:
                raise TgtgApiError(data)

    async def poll_login(self, email: str, polling_id: str) -> Credentials:
        POLLING_INTERVAL = seconds(5)
        POLLING_MAX_TRIES = minutes(2) // POLLING_INTERVAL

        logger.info("Click the link in your email to continue...")

        for _ in range(POLLING_MAX_TRIES):
            data = await self._post(
                TgtgApi.AUTH_BY_POLLING,
                json={"device_type": self.DEVICE_TYPE, "email": email, "request_polling_id": polling_id},
            )

            if data:
                logger.success("Successfully logged in")
                return Credentials.from_json(data)

            logger.debug("Sleeping for {}...", humanize.precisedelta(POLLING_INTERVAL.py_timedelta()))
            await anyio.sleep(POLLING_INTERVAL.in_seconds())

        raise TgtgLoginError("Max polling tries reached")

    async def logout(self) -> None:
        await self._post(TgtgApi.AUTH_LOGOUT)

    async def refresh_credentials(self, *, force: bool = False) -> None:
        if not (force or self.credentials.needs_refresh()):
            return

        logger.debug("Forcing credentials refresh..." if force else "Refreshing credentials...")
        data = await self._post(TgtgApi.TOKEN_REFRESH, json={"refresh_token": self.credentials.refresh_token})
        self.credentials = Credentials.from_json(data)
        logger.debug("Successfully refreshed credentials")

    async def get_startup_data(self) -> JSON:
        return await self._post(TgtgApi.APP_ON_STARTUP)

    async def export_user_data(self) -> None:
        await self._post(TgtgApi.USER_DATA_EXPORT, self.user_id, json={"email": self.email})

    async def delete_user(self, confirmation: str = "") -> None:
        if confirmation != "I KNOW WHAT I'M DOING":
            raise ValueError("Are you sure?")
        await self._post(TgtgApi.USER_DELETE, self.user_id, json={"email": self.email})

    async def change_user_email(self, new_email: str) -> None:
        await self._post(TgtgApi.USER_EMAIL_CHANGE, json={"new_email": new_email})

    async def get_user_email_status(self) -> JSON:
        return await self._post(TgtgApi.USER_EMAIL_STATUS)

    async def get_user_profile(self) -> JSON:
        return await self._post(TgtgApi.USER_PROFILE)

    async def _check_user_profile(self) -> None:
        profile = await self.get_user_profile()
        for key in "co2e_saved", "money_saved":
            del profile[key]
        for key in ("latest_completed_order",):
            if key in profile:
                del profile[key]

        if profile["show_special_reward_card"] is False:
            del profile["show_special_reward_card"]
        if profile["feature_cards"] == {"cards": []}:
            del profile["feature_cards"]
        if profile["feature_details"] == [
            {"type": "ORDERS", "state": "ACTIVE"},
            {
                "type": "C2C_REFERRAL_ALWAYS_ON_INCENTIVIZED",
                "state": "ACTIVE",
                "c2c_referral_details": {
                    "expiry_date": "2050-12-31T23:59:00Z",
                    "voucher_value": {"code": "CAD", "minor_units": 200, "decimals": 2},
                },
            },
            {"type": "IMPACT_TRACKER", "state": "ACTIVE"},
        ]:
            del profile["feature_details"]
        if profile["voucher_tooltip"] == {
            "show_new_voucher_tooltip": False,
            "show_expiring_soon_voucher_tooltip": False,
        }:
            del profile["voucher_tooltip"]

        if profile:
            logger.warning("User profile<normal>: {}</normal>", profile)

    async def set_user_device(self) -> None:
        await self._post(TgtgApi.USER_SET_DEVICE, json={"device_id": self.device_id})

    async def get_invitation_status(self, order_id: str) -> JSON:
        return await self._post(TgtgApi.INVITATION_STATUS, order_id)

    async def get_invitation_link_status(self, invitation_uuid: str) -> JSON:
        return await self._post(TgtgApi.INVITATION_LINK_STATUS, invitation_uuid)

    async def get_order_from_invitation(self, invitation_id: int) -> JSON:
        return await self._post(TgtgApi.INVITATION_ORDER_STATUS, invitation_id)

    async def accept_invitation(self, invitation_uuid: str) -> JSON:
        return await self._post(TgtgApi.INVITATION_ACCEPT, invitation_uuid)

    async def create_invitation(self, order_id: str) -> JSON:
        return await self._post(TgtgApi.INVITATION_CREATE, order_id)

    async def disable_invitation(self, invitation_id: int) -> JSON:
        return await self._post(TgtgApi.INVITATION_DISABLE, invitation_id)

    async def return_invitation(self, invitation_id: int) -> JSON:
        return await self._post(TgtgApi.INVITATION_RETURN, invitation_id)

    async def get_favorites(self) -> list[Favorite]:
        return [fave async for fave in self._get_favorites()]

    async def _get_favorites(
        self,
        *,
        page_size: int = 50,  # Even if >50, server responds with at most 50 favorites
    ) -> AsyncGenerator[Favorite]:
        for page_num in count():
            data = await self._post(
                TgtgApi.FAVORITES,
                json={
                    "origin": self.LOCATION,
                    "radius": float(self.RADIUS),
                    "paging": {"page": page_num, "size": page_size},
                    "bucket": {"filler_type": "Favorites"},
                    "filters": [],
                },
            )

            page = data.get("mobile_bucket", {}).get("items", [])
            for fave in map(Favorite.from_json, page):
                yield fave

            assert "has_more" not in data
            if len(page) < page_size:
                break

    async def get_item(self, item_id: int) -> Item:
        data = await self._post(TgtgApi.ITEM_STATUS, item_id, json={"origin": self.LOCATION})
        return Item.from_json(data)  # type: ignore[return-value]

    @overload
    async def _set_favorite(self, item: Favorite, /, *, is_favorite: bool) -> None: ...
    @overload
    async def _set_favorite(self, item_id: int, /, *, is_favorite: bool) -> None: ...
    async def _set_favorite(self, item_or_id: Favorite | int, *, is_favorite: bool) -> None:
        item_id = item_or_id.id if isinstance(item_or_id, Favorite) else item_or_id

        await self._post(TgtgApi.ITEM_FAVORITE, item_id, json={"is_favorite": is_favorite})

    @overload
    async def favorite(self, item: Favorite, /) -> None: ...
    @overload
    async def favorite(self, item_id: int, /) -> None: ...
    async def favorite(self, item_or_id: Favorite | int) -> None:
        await self._set_favorite(item_or_id, is_favorite=True)

    @overload
    async def unfavorite(self, item: Favorite, /) -> None: ...
    @overload
    async def unfavorite(self, item_id: int, /) -> None: ...
    async def unfavorite(self, item_or_id: Favorite | int) -> None:
        await self._set_favorite(item_or_id, is_favorite=False)

    @overload
    async def reserve(self, item: Favorite, /, quantity: int = 1) -> Reservation: ...
    @overload
    async def reserve(self, item_id: int, /, quantity: int = 1) -> Reservation: ...
    async def reserve(self, item_or_id: Favorite | int, quantity: int = 1) -> Reservation:
        item_id = item_or_id.id if isinstance(item_or_id, Favorite) else item_or_id
        if quantity <= 0:
            raise ValueError(quantity)

        data = await self._post(TgtgApi.ORDER_CREATE, item_id, json={"item_count": quantity})

        match data["state"]:
            case "SALE_CLOSED":
                raise TgtgSaleClosedError
            case "SOLD_OUT":
                raise TgtgSoldOutError
            case "USER_BLOCKED":
                item = await self.get_item(item_id)
                assert item.blocked_until, item.blocked_until
                logger.error(
                    "Reservation blocked for<normal>: {}</normal>",
                    humanize.precisedelta((item.blocked_until - Instant.now()).py_timedelta()),
                )
                raise TgtgReservationBlockedError
            case "INSUFFICIENT_STOCK":
                item = await self.get_item(item_id)
                logger.error(
                    "Insufficient stock<normal>: <bold>{}</bold> available but <bold>{}</bold> requested</normal>",
                    item.num_available,
                    quantity,
                )
                return await self.reserve(item, item.max_quantity)
            case "OVER_USER_WINDOW_LIMIT":
                item = await self.get_item(item_id)
                logger.error(
                    "Purchase limit exceeded<normal>: <bold>{}</bold> allowed but <bold>{}</bold> requested</normal>",
                    item.purchase_limit,
                    quantity,
                )
                assert item.purchase_limit, item.purchase_limit
                if quantity <= item.purchase_limit:
                    raise TgtgLimitExceededError
                return await self.reserve(item, item.max_quantity)
            case "SUCCESS":
                return Reservation.from_json(data["order"])
            case _:
                raise TgtgApiError(data)

    @overload
    async def abort_reservation(self, reservation: Reservation, /) -> JSON: ...
    @overload
    async def abort_reservation(self, reservation_id: str, /) -> JSON: ...
    async def abort_reservation(self, reservation_or_id: Reservation | str) -> JSON:
        reservation_id = reservation_or_id.id if isinstance(reservation_or_id, Reservation) else reservation_or_id

        data = await self._post(TgtgApi.ORDER_ABORT, reservation_id, json={"cancel_reason_id": 1})

        match data["state"]:
            case "ALREADY_ABORTED":
                raise TgtgAlreadyAbortedError
            case "SUCCESS":
                return data
            case _:
                raise TgtgApiError(data)

    async def get_orders(self) -> list[JSON]:
        return [order async for order in self._get_orders()]

    async def _get_orders(self, *, page_size: int = 20) -> AsyncGenerator[JSON]:
        async def pages(page_size: int) -> AsyncGenerator[JSON]:
            yield (page := await self._post(TgtgApi.ORDERS, json={"paging": {"size": page_size}}))

            while page["has_more"]:
                yield (
                    page := await self._post(
                        TgtgApi.ORDERS,
                        json={
                            "paging": {
                                "size": page_size,
                                "next_page_year": page["next_page_year"],
                                "next_page_month": page["next_page_month"],
                            }
                        },
                    )
                )

        async for page in pages(page_size):
            for month in page["orders_per_month"]:
                for order in month["orders"]:
                    yield order

    async def get_active_orders(self) -> list[JSON]:
        data = await self._post(TgtgApi.ORDERS_ACTIVE)
        assert not data["has_more"], data["has_more"]

        orders: list[JSON] = data["orders"]
        return orders

    async def get_order(self, order_id: str) -> JSON:
        return await self._post(TgtgApi.ORDER_STATUS, order_id)

    async def _get_order_short(self, order_id: str) -> JSON:
        return await self._post(TgtgApi.ORDER_STATUS_SHORT, order_id)

    async def cancel_order(self, order_id: str) -> JSON:
        data = await self._post(TgtgApi.ORDER_CANCEL, order_id, json={"cancel_reason_id": 1})

        match data["state"]:
            case "CANCEL_DEADLINE_EXCEEDED":
                raise TgtgCancelDeadlineError
            case "SUCCESS":
                del data["order"]
                return data
            case _:
                raise TgtgApiError(data)

    async def cancel_order_via_support(self, order_id: str, message: str = "Please cancel my order") -> JSON:
        data = await self._post(
            TgtgApi.SUPPORT_REQUEST,
            json={
                "file_urls": [],
                "message": message,
                "subject": "I want to cancel my order",
                "reason": "BAD_ORDER_EXPERIENCE",
                "topic": "CANCEL_ORDER",
                "order_id": order_id,
                "refunding_types": ["VOUCHER", "ORIGINAL_PAYMENT", "REFUSE_REFUND"],
                "confirmation_required_for_duplicate_requests": True,
            },
        )

        match data["support_request_state"]:
            case "ORDER_CANCELLED":
                del data["brief_order"]
                return data
            case _:
                raise TgtgApiError(data)

    @overload
    async def _pay(self, reservation: Reservation, /, authorizations: Iterable[JSON]) -> list[Payment]: ...
    @overload
    async def _pay(self, reservation_id: str, /, authorizations: Iterable[JSON]) -> list[Payment]: ...
    async def _pay(self, reservation_or_id: Reservation | str, authorizations: Iterable[JSON]) -> list[Payment]:
        reservation_id = reservation_or_id.id if isinstance(reservation_or_id, Reservation) else reservation_or_id

        data = await self._post(TgtgApi.ORDER_PAY, reservation_id, json={"authorizations": list(authorizations)})
        return list(map(Payment.from_json, data["payments"]))

    async def pay(self, reservation: Reservation) -> list[Payment]:
        vouchers = await self.get_active_vouchers()
        if not vouchers:
            raise TgtgPaymentError("No vouchers available")
        vouchers = [
            voucher
            for voucher in vouchers
            if isinstance(voucher, MultiUseVoucher) and voucher.amount.code == reservation.total_price.code
        ]
        if not vouchers:
            raise TgtgPaymentError(f"No {reservation.total_price.code} vouchers available")

        authorizations: list[JSON] = []
        for voucher, running_amount in zip(vouchers, accumulate(voucher.amount for voucher in vouchers), strict=True):  # type: ignore[attr-defined]
            authorizations.append(
                {
                    "authorization_payload": {
                        "voucher_id": str(voucher.id),
                        "save_payment_method": False,
                        "type": "voucherAuthorizationPayload",
                    },
                    "payment_provider": "VOUCHER",
                    "return_url": "adyencheckout://com.app.tgtg.itemview",
                    "amount": asdict(voucher.amount),  # type: ignore[attr-defined]
                }
            )
            if running_amount.minor_units >= reservation.total_price.minor_units:
                overage = running_amount - reservation.total_price
                authorizations[-1]["amount"]["minor_units"] -= overage.minor_units
                break
        else:
            raise TgtgPaymentError("Insufficient voucher balance")

        payments = await self._pay(reservation, authorizations)
        logger.debug(payments)
        while any(payment.state == Payment.State.AUTHORIZATION_INITIATED for payment in payments):
            await anyio.sleep(1)
            payments = await self.get_order_payment_status(reservation.id)
            logger.debug(payments)

        if failed := [payment for payment in payments if payment.state == Payment.State.FAILED]:
            raise TgtgPaymentError({payment.failure_reason for payment in failed})
        assert all(payment.state in {Payment.State.CAPTURED, Payment.State.FULLY_REFUNDED} for payment in payments), (
            payments
        )
        return payments

    async def get_payment_status(self, payment_id: int) -> Payment:
        data = await self._post(TgtgApi.PAYMENT_STATUS, payment_id)
        return Payment.from_json(data)

    async def get_order_payment_status(self, order_id: str) -> list[Payment]:
        data = await self._post(TgtgApi.ORDER_PAYMENT_STATUS, order_id)
        return list(map(Payment.from_json, data["payments"]))

    async def get_rewards(self) -> list[JSON]:
        data = await self._post(TgtgApi.REWARDS)
        rewards: list[JSON] = data["rewards"]
        return rewards

    async def get_active_vouchers(self) -> list[Voucher]:
        data = await self._post(TgtgApi.VOUCHERS_ACTIVE)
        return list(map(Voucher.from_json, data["vouchers"]))

    async def get_used_vouchers(self) -> list[Voucher]:
        data = await self._post(TgtgApi.VOUCHERS_USED)
        return list(map(Voucher.from_json, data["vouchers"]))

    async def add_voucher(self, voucher_code: str) -> JSON:
        return await self._post(
            TgtgApi.VOUCHER_ADD, json={"activation_code": voucher_code, "device_id": self.device_id}
        )

    async def get_voucher(self, voucher_id: int) -> Voucher:
        data = await self._post(TgtgApi.VOUCHER_STATUS, voucher_id)
        return Voucher.from_json(data["voucher"])
