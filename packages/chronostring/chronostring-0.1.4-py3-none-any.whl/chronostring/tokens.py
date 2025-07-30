from abc import ABC
from typing import List, Type
from datetime import date, time, datetime


class Token(ABC):

    class_char: str

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not getattr(cls, "abstract", False) and (
            not hasattr(cls, "class_char")
            or not isinstance(cls.class_char, str)
        ):
            raise TypeError(
                f"{cls.__name__} must define a class-level "
                "'class_char' of type str."
            )

    def get_chrono_results(self):
        return []


TokenList = List[Token]


class DateToken(Token):

    class_char = "D"

    def __init__(self, date: date, raw: str):
        self._date = date
        self.raw = raw

    @property
    def date(self) -> date:
        return self._date

    def __str__(self):
        return "<" + self.__class__.__name__ + ":" + str(self._date) + ">"

    def get_chrono_results(self):
        return [self._date]


class TimeToken(Token):

    class_char = "T"

    def __init__(self, time: time, raw: str):
        self._time = time
        self.raw = raw

    @property
    def time(self) -> time:
        return self._time

    def __str__(self):
        return "<" + self.__class__.__name__ + ":" + str(self._time) + ">"

    def get_chrono_results(self):
        return [self._time]


class TimeIntervalToken(Token):

    class_char = "i"

    def __init__(self, time1, time2: time, src: TokenList = None):
        self._time1 = time1
        self._time2 = time2
        self.src = src

    @property
    def start(self) -> time:
        return self._time1

    @property
    def end(self) -> time:
        return self._time2

    def __str__(self):
        return (
            "<"
            + self.__class__.__name__
            + ":"
            + str(self.start)
            + " - "
            + str(self.end)
            + ">"
        )

    def get_chrono_results(self):
        return [(self.start, self.end)]


class DateTimeToken(Token):

    class_char = "r"

    def __init__(self, datetime: datetime, src: TokenList = None):
        self._datetime = datetime
        self.src = src

    @property
    def datetime(self) -> datetime:
        return self._datetime

    def __str__(self):
        return "<" + self.__class__.__name__ + ":" + str(self.datetime) + ">"

    def get_chrono_results(self):
        return [self.datetime]


class SlotToken(Token):

    class_char = "s"

    def __init__(self, datetime1, datetime2: datetime, src: TokenList = None):
        self._datetime1 = datetime1
        self._datetime2 = datetime2
        self.src = src

    @property
    def start(self) -> datetime:
        return self._datetime1

    @property
    def end(self) -> datetime:
        return self._datetime2

    def __str__(self):
        return (
            "<"
            + self.__class__.__name__
            + ":"
            + str(self.start)
            + "-"
            + str(self.end)
            + ">"
        )

    def get_chrono_results(self):
        return [(self.start, self.end)]


class RawStringToken(Token):

    class_char = "§"

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return "<" + self.__class__.__name__ + ":" + self.text + ">"


class PartialTimeToken(RawStringToken):

    class_char = "t"

    def __init__(
        self,
        raw: str,
        hour: int = None,
        minute: int = None,
        second: int = None,
    ):
        super().__init__(raw)
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self):
        return (
            "<"
            + self.__class__.__name__
            + ":"
            + str(self.hour)
            + ":"
            + str(self.minute)
            + ":"
            + str(self.second)
            + " ("
            + str(self.text)
            + ")>"
        )

    def consolidate_time(self, context: time) -> TimeToken:
        t = time(
            context.hour if self.hour is None else self.hour,
            context.minute if self.minute is None else self.minute,
            context.second if self.second is None else self.second,
        )
        return TimeToken(raw=self.text, time=t)


class PartialDateToken(RawStringToken):

    class_char = "d"

    def __init__(
        self,
        raw: str,
        year: int = None,
        month: int = None,
        day: int = None,
        weekday: str = None,
    ):
        super().__init__(raw)
        self.year = year
        self.month = month
        self.day = day
        self.weekday = weekday

    def __str__(self):
        return (
            "<"
            + self.__class__.__name__
            + ":"
            + str(self.year)
            + ", "
            + str(self.month)
            + ", "
            + str(self.day)
            + " ("
            + str(self.text)
            + ")>"
        )

    def consolidate_date(self, context: date) -> DateToken:
        d = date(
            context.year if self.year is None else self.year,
            context.month if self.month is None else self.month,
            context.day if self.day is None else self.day,
        )
        # adjust year by proximity
        if self.year is None:
            dates = [date(d.year + x, d.month, d.day) for x in [-1, 0, 1]]
            dates = [(abs((d - context).days), d) for d in dates]
            d = min(dates, key=lambda x: x[0])[1]

        return DateToken(raw=self.text, date=d)


class IntToken(PartialDateToken, PartialTimeToken):

    class_char = "1"

    def __init__(self, raw: str, value: int):
        PartialDateToken.__init__(self, raw=raw, day=value)
        PartialTimeToken.__init__(self, raw=raw, hour=value)

    def __str__(self):
        return (
            "<"
            + self.__class__.__name__
            + ":"
            + str(self.day)
            + " ("
            + str(self.text)
            + ")>"
        )


class FixedStringToken(Token):
    abstract = True

    substr: str

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not getattr(cls, "abstract", False) and (
            not hasattr(cls, "substr") or not isinstance(cls.substr, str)
        ):
            raise TypeError(
                f"{cls.__name__} must define a class-level "
                "'substr' of type str."
            )

    def __str__(self):
        return "<" + self.__class__.__name__ + ":" + self.substr + ">"


class ConjunctionToken(FixedStringToken):
    abstract = True


class AdditiveConjunctionToken(ConjunctionToken):
    class_char = "&"
    abstract = True


class NotSupportedToken(FixedStringToken):
    class_char = "x"
    abstract = True


class IgnoredToken(FixedStringToken):
    class_char = " "
    abstract = True


class IntervalConjunctionToken(ConjunctionToken):
    class_char = "~"
    abstract = True


class PrecisionConjunctionToken(ConjunctionToken):
    class_char = "+"
    abstract = True


class ExceptionNotSupportedToken(Exception):
    def __init__(self, t: NotSupportedToken):
        self._t = t

    def __str__(self):
        return "ExceptionNotSupportedToken: " + str(self._t)


class TokenLanguagePack(object):

    not_supported: List[Type[NotSupportedToken]]

    ignored_conjunctions: List[Type[IgnoredToken]]

    conjunctions: List[Type[IntervalConjunctionToken]]

    def __init__(self):
        super().__init__()

        self._token_from_str = {}
        for t in self.tokens:
            self._token_from_str[t.substr] = t

    def token_from_str(self, txt: str) -> Token:
        if txt in self._token_from_str:
            t = self._token_from_str[txt]()
            if isinstance(t, NotSupportedToken):
                raise ExceptionNotSupportedToken(t)
            return t
        else:
            return RawStringToken(txt)

    @property
    def tokens(self):
        return (
            self.conjunctions + self.not_supported + self.ignored_conjunctions
        )

    @property
    def token_strings(self):
        return [x.substr for x in self.tokens]


def get_token_pack(lang: str = "fr") -> TokenLanguagePack:
    if lang == "fr":
        from .tokens_fr import FrenchTokens

        return FrenchTokens()
    else:
        raise ValueError("Unsupported language")
