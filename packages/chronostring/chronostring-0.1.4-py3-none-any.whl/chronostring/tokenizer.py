from typing import Type
from .tokens import (
    TokenList,
    TokenLanguagePack,
    get_token_pack,
)


class Tokenizer:

    def __init__(self, debug: bool = False):
        self.token_pack = None
        self._debug = debug

    @property
    def token_pack(self) -> TokenLanguagePack:
        return self._token_pack

    @token_pack.setter
    def token_pack(self, tp: Type[TokenLanguagePack]) -> None:
        self._token_pack = tp

    def process(self, text: str) -> TokenList:
        import re

        # init structure
        if self._token_pack is None:
            self._token_pack = get_token_pack()

        # prepare input
        text = " " + re.sub("(\n|,)", " , ", re.sub("(\t| )", " ", text)) + " "

        # detect each string defined in the pack as a known token
        pattern = re.compile(
            r"[ \t]({})[ \t]".format("|".join(self._token_pack.token_strings)),
            re.IGNORECASE,
        )
        last_end = 0
        for match in pattern.finditer(text):
            if match.start() > last_end:
                yield self._token_pack.token_from_str(
                    text[last_end : match.start()].strip()
                )
            yield self._token_pack.token_from_str(match.group(1))
            last_end = match.end()
        if last_end < len(text):
            yield self._token_pack.token_from_str(text[last_end:].strip())
