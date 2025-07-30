from abc import ABC, abstractmethod
import re
from typing import List
from .tokens import (
    TokenList,
    TokenLanguagePack,
    RawStringToken,
    IntToken,
)
from datetime import date


class ExceptionParsingError(Exception):
    def __init__(self, t: TokenList):
        self._t = t

    def __str__(self):
        return "ExceptionParsingError: " + str(self._t)


class Processor(ABC):

    def __init__(self, debug: bool = False):
        self.debug = debug

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, d):
        self._debug = d

    @classmethod
    @abstractmethod
    def process(
        cls, input: TokenList, pack: TokenLanguagePack, context: date
    ) -> TokenList:
        pass


class RemoveIgnoredTokensProcessor(Processor):

    @classmethod
    def process(
        cls, input: TokenList, pack: TokenLanguagePack, context: date
    ) -> TokenList:
        for token in input:
            if not isinstance(token, tuple(pack.ignored_conjunctions)):
                yield token


class IntegerProcessor(Processor):
    suffixes = []

    @classmethod
    def is_integer(cls, txt):
        if txt.isdigit():
            return True
        for s in cls.suffixes:
            if txt.endswith(s) and txt[: -len(s)].isdigit():
                return True
        return False

    @classmethod
    def process(
        cls, input: TokenList, pack: TokenLanguagePack, context: date
    ) -> TokenList:
        for token in input:
            if type(token) is RawStringToken and cls.is_integer(token.text):
                v = int(re.sub(r"[^\d\.]", "", token.text))
                if v >= 0:
                    yield IntToken(raw=token.text, value=v)
                else:
                    yield token
            else:
                yield token


class RegexProcessor(Processor, ABC):
    regex: str

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not getattr(cls, "abstract", False) and (
            not hasattr(cls, "regex") or not isinstance(cls.regex, str)
        ):
            raise TypeError(
                f"{cls.__name__} must define a class-level "
                "'regex' of type str."
            )

    def to_charlist(tokens):
        return "".join([t.class_char for t in tokens])

    @classmethod
    @abstractmethod
    def convert_match(cls, tokens: TokenList, context: date) -> TokenList:
        pass

    @classmethod
    def intermediate_tokens(
        cls, tokens: TokenList, start: int, end: int
    ) -> TokenList:
        return tokens[start:end]

    @classmethod
    def process(
        cls, input: TokenList, pack: TokenLanguagePack, context: date
    ) -> TokenList:
        tlist = list(input)
        txt = RegexProcessor.to_charlist(tlist)

        pattern = re.compile(cls.regex)

        last_end = 0
        for match in pattern.finditer(txt):
            if match.start() > last_end:
                yield from cls.intermediate_tokens(
                    tlist, last_end, match.start()
                )
            yield from cls.convert_match(
                cls,
                cls.intermediate_tokens(tlist, match.start(), match.end()),
                context,
            )
            last_end = match.end()
        if last_end < len(txt):
            yield from cls.intermediate_tokens(tlist, last_end, None)


def get_processors(lang: str = "fr") -> List[Processor]:
    if lang == "fr":
        from .processors_fr import french_processors

        return french_processors
    else:
        raise ValueError("Unsupported language")
