from typing import Union, List, Tuple
from .tokens import TokenList
from datetime import datetime, date

ChronoResult = Union[date, datetime, Tuple[datetime, datetime]]
ChronoResultList = List[ChronoResult]


class ChronoInterpreter:

    def __init__(self, debug: bool = False):
        self.debug = debug

    def process(self, tokens: TokenList) -> ChronoResultList:
        for t in tokens:
            if self.debug:
                print(t)
            for dt in t.get_chrono_results():
                yield dt
