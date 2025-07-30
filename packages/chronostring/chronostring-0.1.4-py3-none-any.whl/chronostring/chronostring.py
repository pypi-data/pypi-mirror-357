from .tokenizer import Tokenizer
from .tokens import get_token_pack
from datetime import date, datetime
from .interpreter import ChronoInterpreter, ChronoResultList
from .processors import get_processors


class DateParser:

    def __init__(self, context: date = None, debug: bool = False):
        self._debug = debug

        self._context = context
        self._tokenizer = Tokenizer(debug=self._debug)
        self._language = "fr"
        self._token_pack = None

        self._processors = []
        self._interpreter = ChronoInterpreter(debug=self._debug)

    @property
    def context(self) -> datetime:
        return self._context

    @property
    def language(self) -> str:
        return self._language

    @context.setter
    def context(self, ref: datetime) -> None:
        self._context = ref

    @language.setter
    def language(self, language: str = None) -> None:
        if language is not None:
            self._language = language
        self._token_pack = get_token_pack(self._language)
        self._processors = get_processors(self._language)

    def parse(self, text: str) -> ChronoResultList:
        # clear processors
        for p in self._processors:
            p.clear()

        # init token pack and processor pack
        if self._token_pack is None or len(self._processors) == 0:
            self.language = "fr"

        # build initial token list
        self._tokenizer.token_pack = self._token_pack
        tokens = self._tokenizer.process(text)

        # apply processors
        for p in self._processors:
            p.debug = self._debug
            tokens = p.process(tokens, self._token_pack, self._context)

        # return datetimes and intervals
        return list(self._interpreter.process(tokens))


def parse_dates(
    text: str, context: date = None, debug: bool = False
) -> ChronoResultList:
    t = DateParser(date.today() if context is None else context, debug=debug)
    return t.parse(text)
