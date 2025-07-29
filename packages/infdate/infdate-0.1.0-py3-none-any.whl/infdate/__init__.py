# -*- coding: utf-8 -*-

"""
infdate: a wrapper around standard library’s datetime.date objects,
capable of representing positive and negative infinity
"""

import datetime
import math

from typing import final, overload, Any, Final, TypeVar

INFINITY: Final = math.inf
NEGATIVE_INFINITY: Final = -math.inf

INFINITE_DATE_DISPLAY: Final = "<inf>"
NEGATIVE_INFINITE_DATE_DISPLAY: Final = "<-inf>"

ISO_DATE_FORMAT: Final = "%Y-%m-%d"
ISO_DATETIME_FORMAT_UTC: Final = f"{ISO_DATE_FORMAT}T%H:%M:%S.%f%Z"

D = TypeVar("D", bound="Date")


class DateMeta(type):
    """Date metaclass"""

    @property
    def min(cls: type[D], /) -> D:  # type: ignore[misc]
        """Minimum possible Date"""
        return cls(NEGATIVE_INFINITY)

    @property
    def max(cls: type[D], /) -> D:  # type: ignore[misc]
        """Maximum possible Date"""
        return cls(INFINITY)


class Date(metaclass=DateMeta):
    """Date object capable of representing negative or positive infinity"""

    resolution = 1

    @overload
    def __init__(self: D, year_or_strange_number: float, /) -> None: ...
    @overload
    def __init__(
        self: D, year_or_strange_number: int, month: int, day: int, /
    ) -> None: ...
    @final
    def __init__(
        self: D, year_or_strange_number: int | float, /, month: int = 0, day: int = 0
    ) -> None:
        """Create a date-like object"""
        if isinstance(year_or_strange_number, int):
            self.__wrapped_date_obj: datetime.date | None = datetime.date(
                int(year_or_strange_number), month, day
            )
            self.__ordinal: float | int = self.__wrapped_date_obj.toordinal()
        elif math.isnan(year_or_strange_number):
            raise ValueError("Cannot instantiate from NaN")
        elif year_or_strange_number in (
            INFINITY,
            NEGATIVE_INFINITY,
        ):
            self.__ordinal = year_or_strange_number
            self.__wrapped_date_obj = None
        else:
            raise ValueError("Cannot instantiate from a regular deterministic float")
        #

    def toordinal(self: D) -> float | int:
        """to ordinal (almost like datetime.date.toordinal())"""
        return self.__ordinal

    def get_date_object(self: D) -> datetime.date:
        """Return the wrapped date object"""
        if isinstance(self.__wrapped_date_obj, datetime.date):
            return self.__wrapped_date_obj
        #
        raise ValueError("Non-deterministic date")

    @property
    def year(self: D) -> int:
        """shortcut: year"""
        return self.get_date_object().year

    @property
    def month(self: D) -> int:
        """shortcut: month"""
        return self.get_date_object().month

    @property
    def day(self: D) -> int:
        """shortcut: day"""
        return self.get_date_object().day

    def replace(self: D, /, year: int = 0, month: int = 0, day: int = 0) -> D:
        """Return a copy with year, month, and/or date replaced"""
        internal_object = self.get_date_object()
        return self.factory(
            internal_object.replace(
                year=year or internal_object.year,
                month=month or internal_object.month,
                day=day or internal_object.day,
            )
        )

    def isoformat(self: D) -> str:
        """Date representation in ISO format"""
        return self.strftime(ISO_DATE_FORMAT)

    def strftime(self: D, fmt: str, /) -> str:
        """String representation of the date"""
        try:
            date_object = self.get_date_object()
        except ValueError as error:
            if self.__ordinal == INFINITY:
                return INFINITE_DATE_DISPLAY
            #
            if self.__ordinal == NEGATIVE_INFINITY:
                return NEGATIVE_INFINITE_DATE_DISPLAY
            #
            raise error from error
        #
        return date_object.strftime(fmt or ISO_DATE_FORMAT)

    __format__ = strftime

    def __bool__(self: D) -> bool:
        """True if a real date is wrapped"""
        return self.__wrapped_date_obj is not None

    def __hash__(self: D) -> int:
        """hash value"""
        return hash(f"date with ordinal {self.__ordinal}")

    def __add__(self: D, delta: int | float, /) -> D:
        """Add other, respecting maybe-nondeterministic values"""
        for observed_item in (delta, self.__ordinal):
            for infinity_form in (INFINITY, NEGATIVE_INFINITY):
                if observed_item == infinity_form:
                    return self.factory(infinity_form)
                #
            #
        #
        return self.fromordinal(int(self.__ordinal) + int(delta))

    @overload
    def __sub__(self: D, other: int | float, /) -> D: ...
    @overload
    def __sub__(self: D, other: D, /) -> int | float: ...
    @final
    def __sub__(self: D, other: D | int | float, /) -> D | int | float:
        """subtract other, respecting possibly nondeterministic values"""
        if isinstance(other, (int, float)):
            return self + -other
        #
        return self.__ordinal - other.toordinal()

    def __lt__(self: D, other: D, /) -> bool:
        """Rich comparison: less"""
        return self.__ordinal < other.toordinal()

    def __le__(self: D, other: D, /) -> bool:
        """Rich comparison: less or equal"""
        return self < other or self == other

    def __gt__(self: D, other: D, /) -> bool:
        """Rich comparison: greater"""
        return self.__ordinal > other.toordinal()

    def __ge__(self: D, other: D, /) -> bool:
        """Rich comparison: greater or equal"""
        return self > other or self == other

    def __eq__(self: D, other, /) -> bool:
        """Rich comparison: equals"""
        return self.__ordinal == other.toordinal()

    def __ne__(self: D, other, /) -> bool:
        """Rich comparison: does not equal"""
        return self.__ordinal != other.toordinal()

    def __repr__(self: D, /) -> str:
        """String representation of the object"""
        try:
            return f"{self.__class__.__name__}({self.year}, {self.month}, {self.day})"
        except ValueError:
            return f"{self.__class__.__name__}({repr(self.__ordinal)})"
        #

    def __str__(self: D, /) -> str:
        """String representation of the date"""
        return self.isoformat()

    @classmethod
    def today(cls: type[D], /) -> D:
        """Today as Date object"""
        return cls.factory(datetime.date.today())

    @classmethod
    def fromisoformat(
        cls: type[D],
        source: str,
        /,
    ) -> D:
        """Create an instance from an iso format representation"""
        lower_source_stripped = source.strip().lower()
        if lower_source_stripped == INFINITE_DATE_DISPLAY:
            return cls(INFINITY)
        #
        if lower_source_stripped == NEGATIVE_INFINITE_DATE_DISPLAY:
            return cls(NEGATIVE_INFINITY)
        #
        return cls.factory(datetime.date.fromisoformat(lower_source_stripped))

    @classmethod
    def fromisocalendar(
        cls: type[D],
        /,
        year: int,
        week: int,
        day: int,
    ) -> D:
        """Create an instance from an iso calendar date"""
        return cls.factory(datetime.date.fromisocalendar(year, week, day))

    @classmethod
    def fromordinal(
        cls: type[D],
        source: float | int,
        /,
    ) -> D:
        """Create an instance from a date ordinal"""
        if isinstance(source, int):
            return cls.factory(datetime.date.fromordinal(source))
        #
        if source in (NEGATIVE_INFINITY, INFINITY):
            return cls(source)
        #
        raise ValueError(f"Invalid source for .fromordinal(): {source!r}")

    @classmethod
    def from_api_data(
        cls: type[D],
        source: Any,
        /,
        *,
        fmt: str = ISO_DATETIME_FORMAT_UTC,
        past_bound: bool = False,
    ) -> D:
        """Create an instance from string or another type,
        assuming infinity in the latter case
        """
        if isinstance(source, str):
            return cls.factory(datetime.datetime.strptime(source, fmt))
        #
        return cls(NEGATIVE_INFINITY if past_bound else INFINITY)

    @overload
    @classmethod
    def factory(cls: type[D], source: datetime.date | datetime.datetime, /) -> D: ...
    @overload
    @classmethod
    def factory(cls: type[D], source: float, /) -> D: ...
    @final
    @classmethod
    def factory(
        cls: type[D], source: datetime.date | datetime.datetime | float, /
    ) -> D:
        """Create a new instance from a datetime.date or datetime.datetime object,
        from
        """
        if isinstance(source, (datetime.date, datetime.datetime)):
            return cls(source.year, source.month, source.day)
        #
        return cls(source)


BEFORE_BIG_BANG: Final = Date.max
SAINT_GLINGLIN: Final = Date.min
