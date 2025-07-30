# chronostring

*chronostring* is a Python library designed to extract dates and times from natural language strings written in *French*. It transforms text like "du 3 au 5 juillet" into Python `datetime` objects, making it easier to process temporal information from unstructured data.

It is designed to handle flexible, informal expressions such as:

- "5 et 6 juin 2024"
- "du 3 au 5 juillet"
- "lundi 4 et mardi 5 mars 2025"
- "les 1er, 2 et 5 juin à 10h"
- "le 8 et le 9 mai"
- "vendredi 12/01/2025 à 18h30"

## Features

- Extracts single dates and date ranges from French strings
- Handles time expressions like "à 18h" or "de 10:00 à 12:00"
- Recognizes partial dates and completes them from context
- Produces clean and structured outputs: each item in the output list is either a date, a datetime or a datetime range.

## How chronostring Works

*chronostring* operates through a [multi-step process](./chronostring/chronostring.py) designed for extracting structured date and time data from natural language strings.

First, the input string is [tokenized](./chronostring/tokenizer.py) into elementary [Token](./chronostring/tokens.py) objects, identifying both literal tokens (such as conjunctions and delimiters) and content-bearing ones (such as partial or complete dates and times).

These tokens are then enriched through a second stage that detects and completes partial dates and times when possible. The next stage involves matching token sequences to known temporal patterns, using a symbolic representation (each token class mapped to a character) and applying regular expressions on these symbolic strings.

Matched patterns are replaced with more complex temporal objects such as datetime, date, or datetime intervals.
This entire processing pipeline is implemented via a series of [processors](./chronostring/processors.py), designed to be chained and optimized with Python's yield mechanism for lazy evaluation and efficiency.

The library also supports internationalization: all language-specific tokens and processors for French are grouped into a separate implementation ([tokens_fr](./chronostring/tokens_fr.py) and [processors_fr](./chronostring/processors_fr.py)), making it easy to extend support for other languages.

## Installation

```bash
pip install chronostring
```

## Usage

```python
from chronostring import parse_dates

text = "Les 5, 6 et 7 juin à 10h"
dates = parse_dates(text)

for dt in dates:
    print(dt)
```
## Test suite

To run the test suite, simply use the command `make test` from the root directory of the project. This command will automatically invoke `pytest` and run all unit tests defined in the [tests/](./tests/) directory. Make sure you have the required dependencies installed beforehand.

## License

This project is licensed under the *GNU Affero General Public License v3.0 or later (AGPL-3.0)*.

See [LICENSE](./LICENSE) for details.

## Authors

See [AUTHORS.md](./AUTHORS.md) for the list of contributors.