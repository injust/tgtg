from __future__ import annotations

import copy
from abc import ABC
from enum import Enum, StrEnum, auto
from functools import wraps
from typing import TYPE_CHECKING, Any, ClassVar, NoReturn, Self, cast, overload, override

from attrs import Attribute, Converter, define, field, fields, frozen
from attrs.converters import optional
from babel.numbers import format_currency
from loguru import logger
from whenever import Instant, SystemDateTime, TimeDelta, ZonedDateTime, minutes

from .utils import Interval, relative_local_datetime

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    type JSON = dict[str, Any]

logger = logger.opt(colors=True)


@overload
def debug[T](from_json: Callable[[type[T], JSON], T]) -> Callable[[type[T], JSON], T]: ...
@overload
def debug[T](from_json: Callable[[type[T], JSON], T | None]) -> Callable[[type[T], JSON], T | None]: ...
def debug[T](from_json: Callable[[type[T], JSON], T | None]) -> Callable[[type[T], JSON], T | None]:
    @wraps(from_json)
    def wrapper(cls: type[T], data: JSON) -> T | None:
        try:
            return from_json(cls, data.copy())
        except Exception:
            logger.opt(depth=1).debug(data)
            raise

    return wrapper


def repr_field(obj: object) -> str:
    match obj:
        case None:
            return repr(None)
        case Enum():
            return obj.name
        case Instant():
            date, time = relative_local_datetime(obj)
            return repr(f"{date} at {time}")
        case Interval() if isinstance(obj.start, ZonedDateTime) and isinstance(obj.end, ZonedDateTime):  # pyright: ignore[reportUnknownMemberType]
            start_date, start_time = relative_local_datetime(obj.start)
            end_date, end_time = relative_local_datetime(obj.end)

            assert obj.start.tz == obj.end.tz, (obj.start.tz, obj.end.tz)
            if obj.start.offset == SystemDateTime.now().offset == obj.end.offset:
                start_tz = ""
                end_tz = ""
            else:
                # TODO(https://github.com/ariebovenberg/whenever/issues/60): Use `ZonedDateTime.tzname()`
                start_tz = " " + cast("str", obj.start.py_datetime().tzname())
                end_tz = " " + cast("str", obj.end.py_datetime().tzname())

            if start_date != end_date:
                return repr(f"{start_date} at {start_time}{start_tz} to {end_date} at {end_time}{end_tz}")
            if start_tz == end_tz:
                return repr(f"{start_date} {start_time}–{end_time}{end_tz}")  # noqa: RUF001
            return repr(f"{start_date} {start_time}{start_tz}–{end_time}{end_tz}")  # noqa: RUF001
        case _:
            return repr(str(obj))


@define(kw_only=True)
class ColorizeMixin:
    @property
    def _non_default_fields(self) -> tuple[tuple[Attribute[object], object], ...]:
        return tuple(
            (field, value) for field in fields(type(self)) if (value := getattr(self, field.name)) != field.default
        )

    def colorize(self) -> str:
        field_repr: list[str] = []

        for field_, value in self._non_default_fields:
            if field_.repr:
                repr_func = repr if field_.repr is True else field_.repr
                field_repr.append(f"{field_.name}=<normal>{repr_func(value)}</normal>")

        return f"{type(self).__name__}(<dim>{', '.join(field_repr)}</dim>)"


@define(kw_only=True)
class Favorite(ColorizeMixin):
    class Tag(StrEnum):
        NEW = "New"

        # Generic tags
        HIDDEN_GEM = "Hidden gem"
        POPULAR = "Popular"
        RARE_FIND = "Rare find"
        SELLING_FAST = "Selling fast"

        # Stateful tags
        CHECK_AGAIN_LATER = "Check again later"
        ENDING_SOON = "Ending soon"
        NOTHING_TODAY = "Nothing today"
        SOLD_OUT = "Sold out"
        X_ITEMS_LEFT = "X left"

        @property
        def is_generic(self) -> bool:
            return self in {self.HIDDEN_GEM, self.POPULAR, self.RARE_FIND, self.SELLING_FAST}

        @property
        def is_state(self) -> bool:
            return self in {
                self.CHECK_AGAIN_LATER,
                self.ENDING_SOON,
                self.NOTHING_TODAY,
                self.SOLD_OUT,
                self.X_ITEMS_LEFT,
            }

        @classmethod
        @debug
        def from_json(cls, data: JSON) -> Favorite.Tag:
            match data["id"]:
                case "GENERIC":
                    tag = cls[data["variant"]]
                case "NOTHING_TO_SAVE_TODAY":
                    tag = cls.NOTHING_TODAY
                case _:
                    tag = cls[data["id"]]

            if tag != cls.X_ITEMS_LEFT:
                assert data["short_text"] == tag, data["short_text"]
            return tag

    id: int = field(
        repr=repr_field,  # TODO(https://github.com/ghostty-org/ghostty/issues/904): Remove `repr` when Ghostty word selection is less greedy
        converter=int,
    )
    name: str
    tag: Tag | None = field(default=Tag.NOTHING_TODAY, repr=repr_field)
    _tags: list[Tag] = field(repr=False, alias="_tags")
    num_available: int = field(default=0, alias="items_available")
    pickup_interval: Interval[ZonedDateTime] | None = field(default=None, repr=repr_field)
    sold_out_at: Instant | None = field(
        default=None,
        repr=repr_field,
        converter=optional(Instant.parse_common_iso),  # type: ignore[misc]
    )
    purchase_end: Instant | None = field(
        default=None,
        repr=repr_field,
        converter=[  # type: ignore[misc]
            optional(Instant.parse_common_iso),
            Converter(
                lambda purchase_end, self: purchase_end
                if (pickup_interval := cast("Favorite", self).pickup_interval) is None
                or pickup_interval.end != purchase_end
                else None,
                takes_self=True,
            ),
        ],
    )

    def __attrs_post_init__(self) -> None:
        assert self.is_selling == (self.num_available > 0), (
            self.id,
            self.tag,
            self._tags,
            self.num_available,
            self.is_selling,
        )

    @classmethod
    @debug
    def from_json(cls, data: JSON) -> Self:
        def build_name(item: JSON, store: JSON) -> str:
            name: list[str] = [store["store_name"].strip()]
            if store_branch := store.get("branch", "").strip():
                name.extend(("-", store_branch))
            item_name = item["name"].strip() or "Surprise Bag"
            name.append(f"({item_name})")

            return " ".join(name)

        def build_pickup_interval(pickup_interval: JSON | None, store: JSON) -> Interval[ZonedDateTime] | None:
            if pickup_interval is None:
                return None

            store_tz: str = store["store_time_zone"]
            return Interval(
                ZonedDateTime.parse_common_iso(f"{pickup_interval['start']}[{store_tz}]"),
                ZonedDateTime.parse_common_iso(f"{pickup_interval['end']}[{store_tz}]"),
            )

        def process_tags(tags: Iterable[Favorite.Tag]) -> Favorite.Tag | None:
            tags = set(tags) - {cls.Tag.NEW}

            # Handle multiple tags
            if states := {tag for tag in tags if tag.is_state}:
                tags = states
                if cls.Tag.CHECK_AGAIN_LATER in tags or cls.Tag.ENDING_SOON in tags:
                    tags.discard(cls.Tag.X_ITEMS_LEFT)

            assert len(tags) <= 1, tags
            return next(iter(tags), None)

        item: JSON = data.pop("item")
        assert not item["can_user_supply_packaging"], item["can_user_supply_packaging"]
        store: JSON = data.pop("store")
        item_tags = list(map(cls.Tag.from_json, data.pop("item_tags")))

        for key in (
            "display_name",
            "pickup_location",
            "distance",
            "favorite",
            "subscribed_to_notification",
            "in_sales_window",
            "new_item",
            "item_type",
        ):
            del data[key]
        for key in "sharing_url", "matches_filters", "item_card", "item_special_reward":
            if key in data:
                del data[key]

        return cls(
            id=item["item_id"],
            name=build_name(item, store),
            _tags=item_tags,
            tag=process_tags(item_tags),
            pickup_interval=build_pickup_interval(data.pop("pickup_interval", None), store),
            **data,
        )

    @property
    def is_selling(self) -> bool:
        if self.tag is None:
            return self.num_available > 0
        selling_states = {self.Tag.ENDING_SOON, self.Tag.X_ITEMS_LEFT}
        return self.tag in selling_states or self.tag.is_generic

    @property
    def is_interesting(self) -> bool:
        fields_ = fields(type(self))
        uninteresting_fields = {fields_.id, fields_.name, *(field for field in fields_ if field.name.startswith("_"))}
        return any(field not in uninteresting_fields for field, _ in self._non_default_fields)

    def colorize_diff(self, old_item: Self) -> str:
        field_repr: list[str] = []

        for field_ in fields(type(self)):
            if field_.repr:
                value = getattr(self, field_.name)
                old_value = getattr(old_item, field_.name)
                if old_value == field_.default == value:
                    continue

                repr_func = repr if field_.repr is True else field_.repr
                field_repr.append(
                    f"{field_.name}={repr_func(value)}"
                    if value == old_value
                    else f"{field_.name}=<normal><bold>{repr_func(value)}</bold></normal>"
                )

        return f"{type(self).__name__}(<dim>{', '.join(field_repr)}</dim>)"


@define(kw_only=True)
class Item(Favorite):
    purchase_limit: int | None = field(default=None, alias="user_purchase_limit")
    next_drop: Instant | None = field(
        default=None,
        repr=repr_field,
        converter=optional(Instant.parse_common_iso),  # type: ignore[misc]
        alias="next_sales_window_purchase_start",
    )
    blocked_until: Instant | None = field(
        default=None,
        repr=repr_field,
        converter=optional(Instant.parse_common_iso),  # type: ignore[misc]
        alias="reservation_blocked_until",
    )

    @property
    def max_quantity(self) -> int:
        return min(self.num_available, self.purchase_limit or self.num_available)

    def to_favorite(self) -> Favorite:
        fave = object.__new__(Favorite)
        for field_ in fields(Favorite):
            object.__setattr__(fave, field_.name, getattr(self, field_.name))
        return fave


@frozen(kw_only=True)
class Payment:
    class State(Enum):
        AUTHORIZATION_INITIATED = auto()
        AUTHORIZED = auto()
        CANCELLED = auto()
        CAPTURED = auto()
        FAILED = auto()
        FULLY_REFUNDED = auto()

    id: int = field(
        repr=repr_field,  # TODO(https://github.com/ghostty-org/ghostty/issues/904): Remove `repr` when Ghostty word selection is less greedy
        converter=int,
        alias="payment_id",
    )
    payment_provider: str
    state: State = field(repr=repr_field, converter=State.__getitem__)  # type: ignore[misc]

    @classmethod
    @debug
    def from_json(cls, data: JSON) -> Payment:
        for key in "order_id", "user_id":
            del data[key]

        match cls.State[data["state"]]:
            case cls.State.FAILED:
                return FailedPayment(**data)
            case _:
                return Payment(**data)


@frozen(kw_only=True)
class FailedPayment(Payment):
    class FailureReason(Enum):
        FAILED = auto()
        PAYMENT_METHOD_EXPIRED = auto()

    failure_reason: FailureReason = field(repr=repr_field, converter=FailureReason.__getitem__)  # type: ignore[misc]

    @override
    @classmethod
    def from_json(cls, data: JSON) -> NoReturn:
        raise NotImplementedError


@frozen(kw_only=True)
class Price:
    code: str
    minor_units: int
    decimals: int

    @classmethod
    @debug
    def from_json(cls, data: JSON) -> Self:
        return cls(**data)

    def __add__(self, other: Price) -> Self:
        if not isinstance(other, Price):  # pyright: ignore[reportUnnecessaryIsInstance]
            return NotImplemented  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
        if self.code != other.code:
            raise ValueError("Incompatible currencies")

        return copy.replace(self, minor_units=self.minor_units + other.minor_units)  # type: ignore[type-var]

    def __sub__(self, other: Price) -> Self:
        if not isinstance(other, Price):  # pyright: ignore[reportUnnecessaryIsInstance]
            return NotImplemented  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
        if self.code != other.code:
            raise ValueError("Incompatible currencies")

        return copy.replace(self, minor_units=self.minor_units - other.minor_units)  # type: ignore[type-var]

    @override
    def __str__(self) -> str:
        return format_currency(self.minor_units / 10**self.decimals, self.code)


@define(kw_only=True)
class Reservation(ColorizeMixin):
    class State(Enum):
        RESERVED = auto()

    id: str
    item_id: int = field(
        repr=repr_field,  # TODO(https://github.com/ghostty-org/ghostty/issues/904): Remove `repr` when Ghostty word selection is less greedy
        converter=int,
    )
    state: State = field(repr=False, converter=State.__getitem__)  # type: ignore[misc]
    quantity: int
    total_price: Price = field(repr=repr_field, converter=Price.from_json)  # type: ignore[misc]
    reserved_at: Instant = field(repr=repr_field, converter=Instant.parse_common_iso)  # type: ignore[misc]

    TTL: ClassVar[TimeDelta] = minutes(4)

    @classmethod
    @debug
    def from_json(cls, data: JSON) -> Self:
        order_line: JSON = data.pop("order_line")

        for key in "user_id", "order_type", "might_be_eligible_for_reward", "is_multi_item":
            del data[key]

        return cls(
            quantity=order_line["quantity"],
            total_price=order_line["total_price"],
            reserved_at=data.pop("reserved_at") + "Z",
            **data,
        )

    @property
    def expires_at(self) -> Instant:
        return self.reserved_at + self.TTL


@frozen(kw_only=True)
class Voucher(ABC):
    class State(Enum):
        ACTIVE = auto()
        USED = auto()

    class Type(Enum):
        EASY = auto()
        REGULAR = auto()
        USER_REFERRAL = auto()

    class Version(Enum):
        COUNTRY_BASED_SINGLE_USE_VOUCHER = auto()
        CURRENCY_BASED_MULTI_USE_VOUCHER = auto()

    id: int = field(
        repr=repr_field,  # TODO(https://github.com/ghostty-org/ghostty/issues/904): Remove `repr` when Ghostty word selection is less greedy
        converter=int,
    )
    name: str
    state: State = field(repr=repr_field, converter=State.__getitem__)  # type: ignore[misc]
    type: Type = field(repr=repr_field, converter=Type.__getitem__)  # type: ignore[misc]
    version: Version = field(repr=False, converter=Version.__getitem__)  # type: ignore[misc]

    @classmethod
    @debug
    def from_json(cls, data: JSON) -> Voucher:  # type: ignore[return]
        if "store_filter_type" in data:
            assert (store_filter_type := data.pop("store_filter_type")) == "NONE", store_filter_type

        for key in "valid_from", "valid_to":
            del data[key]
        for key in "short_description", "terms_link", "country_id":
            if key in data:
                del data[key]

        match cls.Version[data["version"]]:  # type: ignore[exhaustive-match]
            case cls.Version.COUNTRY_BASED_SINGLE_USE_VOUCHER:
                return SingleUseVoucher(**data)
            case cls.Version.CURRENCY_BASED_MULTI_USE_VOUCHER:
                if "items_left" in data:
                    assert not (items_left := data.pop("items_left")), items_left

                return MultiUseVoucher(**data)


@frozen(kw_only=True)
class MultiUseVoucher(Voucher):
    amount: Price = field(repr=repr_field, converter=Price.from_json, alias="current_amount")  # type: ignore[misc]
    original_amount: Price | None = field(default=None, repr=repr_field, converter=optional(Price.from_json))  # type: ignore[misc]

    @override
    @classmethod
    def from_json(cls, data: JSON) -> NoReturn:
        raise NotImplementedError


@frozen(kw_only=True)
class SingleUseVoucher(Voucher):
    max_item_price: Price | None = field(default=None, repr=repr_field, converter=optional(Price.from_json))  # type: ignore[misc]
    items_left: int
    num_items: int | None = field(default=None, alias="number_of_items")

    @override
    @classmethod
    def from_json(cls, data: JSON) -> NoReturn:
        raise NotImplementedError


for tag in Favorite.Tag.__members__.values():
    assert tag == Favorite.Tag.NEW or tag.is_generic or tag.is_state, tag
