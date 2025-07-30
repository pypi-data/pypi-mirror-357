from .processors import (
    Processor,
    RegexProcessor,
    IntegerProcessor,
    RemoveIgnoredTokensProcessor,
    ExceptionParsingError,
)
from .tokens import (
    RawStringToken,
    TokenList,
    DateToken,
    PartialDateToken,
    TimeToken,
    PartialTimeToken,
    TimeIntervalToken,
    DateTimeToken,
    SlotToken,
    TokenLanguagePack,
)
from .utils import remove_accents
import re
from datetime import date, time, datetime, timedelta


class IntegerFrProcessor(IntegerProcessor):
    suffixes = ["er", "e", "eme"]


class DateFrProcessor(Processor):

    def guess_internal(text, list):
        t = remove_accents(text).lower()
        for i, m in enumerate(list):
            if t.startswith(m):
                return i + 1
        return None

    def guess_weekday(text):
        days = [
            "lu",
            "ma",
            "me",
            "je",
            "ve",
            "sa",
            "di",
        ]
        return DateFrProcessor.guess_internal(text, days)

    def guess_month(text):
        mths = [
            "jan",
            "fe",
            "mar",
            "av",
            "mai",
            "juin",
            "juil",
            "ao",
            "sep",
            "oct",
            "nov",
            "dec",
        ]
        return DateFrProcessor.guess_internal(text, mths)

    def parse_french_date(text):
        prefix = None
        weekday = None
        day = None
        month = None
        year = None
        suffix = None
        # format NomJour Numero Mois Année
        m = re.search(
            (
                "(.*?)([a-zA-ZéÉûÛ:.]+)[  ]*([0-9]+)[er]*[  ]*"
                "([a-zA-ZéÉûÛ:.]+)[  ]*([0-9]+)(.*?)"
            ),
            text,
        )
        if m:
            prefix = m.group(1).strip()
            weekday = DateFrProcessor.guess_weekday(m.group(2))
            day = m.group(3)
            month = DateFrProcessor.guess_month(m.group(4))
            year = m.group(5)
            suffix = m.group(6).strip()
        else:
            # format Numero Mois Annee
            m = re.search(
                "(.*?)([0-9]+)[er]*[  ]*([a-zA-ZéÉûÛ:.]+)[  ]*([0-9]+)(.*?)",
                text,
            )
            if m:
                prefix = m.group(1).strip()
                day = m.group(2)
                month = DateFrProcessor.guess_month(m.group(3))
                year = m.group(4)
                suffix = m.group(5).strip()
            else:
                # format Numero Mois Annee
                m = re.search("(.*?)([0-9]+)/([0-9]+)/([0-9]+)(.*?)", text)
                if m:
                    prefix = m.group(1).strip()
                    day = m.group(2)
                    month = int(m.group(3))
                    year = m.group(4)
                    suffix = m.group(5).strip()
                else:
                    # format Numero Mois
                    m = re.search(
                        "(.*?)([0-9]+)[er]*[  ]*([a-zA-ZéÉûÛ:.]+)(.*?)", text
                    )
                    if m:
                        prefix = m.group(1).strip()
                        day = m.group(2)
                        month = DateFrProcessor.guess_month(m.group(3))
                        year = None
                        prefix = m.group(4).strip()
                    else:
                        # format NomJour Numero
                        m = re.search(
                            ("(.*?)([a-zA-ZéÉûÛ:.]+)[  ]*([0-9]+)[er]*(.*?)"),
                            text,
                        )
                        if m:
                            prefix = m.group(1).strip()
                            weekday = DateFrProcessor.guess_weekday(m.group(2))
                            day = None if weekday is None else m.group(3)
                            month = None
                            year = None
                            suffix = m.group(4).strip()

        if day is not None:
            try:
                day = int(day)
            except Exception:
                day = None
            if day >= 32:
                day = None

        if year is not None:
            try:
                year = int(year)
            except Exception:
                year = None

        return year, month, day, weekday, prefix, suffix

    @classmethod
    def process(
        cls, input: TokenList, pack: TokenLanguagePack, context: date
    ) -> TokenList:
        for token in input:
            if isinstance(token, RawStringToken):
                year, month, day, weekday, prefix, suffix = (
                    DateFrProcessor.parse_french_date(token.text)
                )
                if year is not None and month is not None and day is not None:
                    if prefix is not None and len(prefix) > 0:
                        yield RawStringToken(prefix)
                    yield DateToken(date(year, month, day), token.text)
                    if suffix is not None and len(suffix) > 0:
                        yield RawStringToken(suffix)
                elif (
                    month is not None or weekday is not None
                ) and day is not None:
                    if prefix is not None and len(prefix) > 0:
                        yield RawStringToken(prefix)
                    yield PartialDateToken(
                        year=year, month=month, day=day, raw=token.text
                    )
                    if suffix is not None and len(suffix) > 0:
                        yield RawStringToken(suffix)
                else:
                    yield token
            else:
                yield token


class TimeFrProcessor(Processor):

    def parse_french_time(text):

        prefix = None
        h = None
        m = None
        s = None
        suffix = None

        # format heures minutes secondes
        mx = re.search(
            "(.*?)([0-9]+)[ a-zA-Z:.]+([0-9]+)" "[ a-zA-Z:.]+([0-9]+)(.*?)",
            text,
        )
        if mx:
            prefix = mx.group(1)
            h = mx.group(2)
            m = mx.group(3)
            s = mx.group(4)
            suffix = mx.group(5)
        else:
            # format heures minutes
            mx = re.search("(.*?)([0-9]+)[ hH:.]+([0-9]+)(.*?)", text)
            if mx:
                prefix = mx.group(1)
                h = mx.group(2)
                m = mx.group(3)
                s = "0"
                suffix = mx.group(4)
            else:
                # format heures
                mx = re.search("(.*?)([0-9]+)[ ]*[Hh:.](.*?)", text)
                if mx:
                    prefix = mx.group(1)
                    h = mx.group(2)
                    m = "0"
                    s = "0"
                    suffix = mx.group(3)

        if h is not None and m is not None and s is not None:
            try:
                h = int(h)
                m = int(m)
                s = int(s)
            except Exception:
                h = None
                m = None
                s = None
        if h is not None and h >= 24:
            h = None
        if m is not None and m >= 60:
            m = None
        if s is not None and s >= 60:
            s = None
        return h, m, s, prefix, suffix

    @classmethod
    def process(
        cls, input: TokenList, pack: TokenLanguagePack, context: date
    ) -> TokenList:
        for token in input:
            if isinstance(token, RawStringToken):
                h, m, s, prefix, suffix = TimeFrProcessor.parse_french_time(
                    token.text
                )
                if h is not None and m is not None and s is not None:
                    if prefix is not None and len(prefix) > 0:
                        yield RawStringToken(prefix)
                    yield TimeToken(time(h, m, s), token.text)
                    if suffix is not None and len(suffix) > 0:
                        yield RawStringToken(suffix)
                else:
                    yield token
            else:
                yield token


class TimeIntervalProcessor(RegexProcessor):
    regex = ":(1|t|T)(-|à)T"

    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        times = [
            t for t in tokens if isinstance(t, (TimeToken, PartialTimeToken))
        ]
        if len(times) == 2:
            t1 = times[0]
            t2 = times[1]
            if isinstance(t1, PartialTimeToken):
                t1 = t1.consolidate_time(context=t2.time)
            yield TimeIntervalToken(t1.time, t2.time)
        else:
            raise ExceptionParsingError(tokens)


class ExactTimeIntervalProcessor(TimeIntervalProcessor):
    regex = "(t|T)(-|à)T"


class DateIntervalProcessor(RegexProcessor):
    regex = "fDoD"

    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        dates = [t for t in tokens if isinstance(t, DateToken)]
        if len(dates) == 2:
            d1 = dates[0].date
            d2 = dates[1].date
            while d1 <= d2:
                yield DateToken(d1, "")
                d1 = d1 + timedelta(days=1)
        else:
            raise ExceptionParsingError(tokens)


class DateConsolidationProcessor(RegexProcessor):
    regex = "((1|d)[^D]*)D"

    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        dt = [t for t in tokens if isinstance(t, DateToken)]
        if len(dt) == 1:
            for d in tokens:
                if isinstance(d, PartialDateToken):
                    yield d.consolidate_date(context=dt[0].date)
                else:
                    yield d
        else:
            raise ExceptionParsingError(tokens)


class ReverseDateConsolidationProcessor(DateConsolidationProcessor):
    regex = "D((1|d)[^D]*)"


class DateConsolidationByContextProcessor(RegexProcessor):
    regex = ".*"

    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        tlist = list(tokens)
        current = context

        # update starting from the last one
        for i in reversed(range(len(tlist))):
            if isinstance(tlist[i], PartialDateToken):
                tlist[i] = tlist[i].consolidate_date(context=current)
                current = tlist[i].date

        for obj in tlist:
            yield obj


class DateListTimeListProcessor(RegexProcessor):
    regex = "D+(à|§)?(T|i)+"

    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        dates = [t for t in tokens if isinstance(t, DateToken)]
        times = [
            t for t in tokens if isinstance(t, (TimeToken, TimeIntervalToken))
        ]

        if len(dates) != 0 and len(times) != 0:
            for d in dates:
                for t in times:
                    if isinstance(t, TimeToken):
                        yield DateTimeToken(datetime.combine(d.date, t.time))
                    else:
                        if isinstance(t, TimeIntervalToken):
                            if t.start > t.end:
                                yield SlotToken(
                                    datetime.combine(d.date, t.start),
                                    datetime.combine(
                                        d.date + timedelta(days=1), t.end
                                    ),
                                )
                            else:
                                yield SlotToken(
                                    datetime.combine(d.date, t.start),
                                    datetime.combine(d.date, t.end),
                                )
                        else:
                            raise ExceptionParsingError(t)
        else:
            raise ExceptionParsingError(tokens)


class SlotProcessor(RegexProcessor):

    regex = "(f)?ror"

    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        datetimes = [t for t in tokens if isinstance(t, DateTimeToken)]

        if len(datetimes) == 2:
            yield SlotToken(datetimes[0].datetime, datetimes[1].datetime)
        else:
            raise ExceptionParsingError(tokens)


french_processors = [
    # cleaning
    RemoveIgnoredTokensProcessor,
    # build date and time
    DateFrProcessor,
    TimeFrProcessor,
    IntegerFrProcessor,
    # detect time intervals
    TimeIntervalProcessor,
    ExactTimeIntervalProcessor,
    # consolidate dates
    DateConsolidationProcessor,
    ReverseDateConsolidationProcessor,
    DateConsolidationByContextProcessor,
    # detect date intervals
    DateIntervalProcessor,
    # multiple datetimes
    DateListTimeListProcessor,
    # detect slots
    SlotProcessor,
]
