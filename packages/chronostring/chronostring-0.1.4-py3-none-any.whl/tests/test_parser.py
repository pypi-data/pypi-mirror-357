from datetime import date, datetime
from chronostring import parse_dates
import pytest
from chronostring.tokens import ExceptionNotSupportedToken

debug = True


def test_single_date():
    assert parse_dates("le 4 juin 2025", debug=debug) == [date(2025, 6, 4)]


def test_multiple_dates():
    assert parse_dates("les 3, 4 et 5 juillet 2025", debug=debug) == [
        date(2025, 7, 3),
        date(2025, 7, 4),
        date(2025, 7, 5),
    ]


def test_date_with_time():
    assert parse_dates("le 5 juin 2025 à 18h30", debug=debug) == [
        datetime(2025, 6, 5, 18, 30)
    ]


def test_exception():
    with pytest.raises(ExceptionNotSupportedToken):
        parse_dates("du 5 au 10 juin sauf le 7 juin", debug=debug)


def test_date_time_interval():
    assert parse_dates("le 5 juin 2025 de 18h à 20h", debug=debug) == [
        (datetime(2025, 6, 5, 18, 0), datetime(2025, 6, 5, 20, 0))
    ]


def test_partial_dates_completion():
    assert parse_dates(
        "les 5, 6 et 7 juillet", debug=debug, context=date(2025, 8, 1)
    ) == [
        date(2025, 7, 5),
        date(2025, 7, 6),
        date(2025, 7, 7),
    ]


def test_partial_followed_by_time_token():
    result = parse_dates("le 5 à 15h", context=date(2025, 7, 1), debug=debug)
    assert result == [datetime(2025, 7, 5, 15, 0)]


def test_date_range_complete():
    result = parse_dates("du 5 juillet 2025 au 7 juillet 2025", debug=debug)
    assert result == [date(2025, 7, 5), date(2025, 7, 6), date(2025, 7, 7)]


def test_date_range_partial_start():
    result = parse_dates("du 5 au 7 juillet 2025", debug=debug)
    assert result == [date(2025, 7, 5), date(2025, 7, 6), date(2025, 7, 7)]


def test_date_range_partial_start_and_month_only_end():
    result = parse_dates(
        "du 5 au 7 juillet", context=date(2025, 8, 1), debug=debug
    )
    assert result == [date(2025, 7, 5), date(2025, 7, 6), date(2025, 7, 7)]


def test_multiple_partial_dates():
    result = parse_dates("les 5, 6 et 7 juillet 2025", debug=debug)
    assert result == [date(2025, 7, 5), date(2025, 7, 6), date(2025, 7, 7)]


def test_partial_month_then_complete_date():
    result = parse_dates(
        "les 3, 4 et 5 août puis le 10 août 2025", debug=debug
    )
    assert result == [
        date(2025, 8, 3),
        date(2025, 8, 4),
        date(2025, 8, 5),
        date(2025, 8, 10),
    ]


def test_interval_with_times():
    result = parse_dates(
        "du 5 juillet 2025 à 14h au 7 juillet 2025 à 16h", debug=debug
    )
    assert result == [(datetime(2025, 7, 5, 14), datetime(2025, 7, 7, 16))]


def test_partial_dates_with_shared_month_and_times():
    result = parse_dates(
        "les 5 à 14h, 6 à 15h et 7 juillet 2025 à 16h", debug=debug
    )
    assert result == [
        datetime(2025, 7, 5, 14),
        datetime(2025, 7, 6, 15),
        datetime(2025, 7, 7, 16),
    ]


def test_date_list_with_time_only_at_end():
    result = parse_dates("les 5, 6 et 7 juillet 2025 à 18h", debug=debug)
    assert result == [
        datetime(2025, 7, 5, 18),
        datetime(2025, 7, 6, 18),
        datetime(2025, 7, 7, 18),
    ]


def test_interval_with_partial_start_and_time():
    result = parse_dates("du 5 à 13h au 7 juillet 2025 à 16h", debug=debug)
    assert result == [(datetime(2025, 7, 5, 13), datetime(2025, 7, 7, 16))]


def test_date_time_interval2():
    assert parse_dates("le 5 juin 2025 de 18 à 20h", debug=debug) == [
        (datetime(2025, 6, 5, 18, 0), datetime(2025, 6, 5, 20, 0))
    ]


def test_overnight_time_interval():
    assert parse_dates(
        "lundi 5 juillet de 20h à 2h",
        context=date(2025, 8, 1),
        debug=debug,
    ) == [(datetime(2025, 7, 5, 20), datetime(2025, 7, 6, 2))]


def test_date_list_across_new_year():
    assert parse_dates(
        "les 31 décembre et 1 janvier", context=date(2025, 12, 1), debug=debug
    ) == [
        date(2025, 12, 31),
        date(2026, 1, 1),
    ]


# Readme examples


def test_readme_example01():
    result = parse_dates("5 et 6 juin 2024", debug=debug)
    assert result == [
        date(2024, 6, 5),
        date(2024, 6, 6),
    ]


def test_readme_example02():
    result = parse_dates(
        "du 3 au 5 juillet", context=date(2025, 6, 1), debug=debug
    )
    assert result == [
        date(2025, 7, 3),
        date(2025, 7, 4),
        date(2025, 7, 5),
    ]


def test_readme_example03():
    result = parse_dates("lundi 4 et mardi 5 mars 2025", debug=debug)
    assert result == [
        date(2025, 3, 4),
        date(2025, 3, 5),
    ]


def test_readme_example04():
    result = parse_dates(
        "les 1er, 2 et 5 juin à 10h", context=date(2025, 4, 1), debug=debug
    )
    assert result == [
        datetime(2025, 6, 1, 10),
        datetime(2025, 6, 2, 10),
        datetime(2025, 6, 5, 10),
    ]


def test_readme_example05():
    result = parse_dates(
        "le 8 et le 9 mai", context=date(2025, 4, 1), debug=debug
    )
    assert result == [
        date(2025, 5, 8),
        date(2025, 5, 9),
    ]


def test_readme_example06():
    result = parse_dates("vendredi 12/01/2025 à 18h30", debug=debug)
    assert result == [
        datetime(2025, 1, 12, 18, 30),
    ]


# Real life examples

# https://www.milleformes.fr/programme/tenir-0


def test_milleformes():
    for txt, dts in [
        (
            "Samedi 12 et dimanche 13 avril 2025",
            [date(2025, 4, 12), date(2025, 4, 13)],
        ),
        (
            "le vendredi 18 avril à 9h45 et 10h45 et le samedi 19 avril à 9h45",
            [
                datetime(2025, 4, 18, 9, 45),
                datetime(2025, 4, 18, 10, 45),
                datetime(2025, 4, 19, 9, 45),
            ],
        ),
        (
            "le samedi 19 avril à 11h et 15h45",
            [datetime(2025, 4, 19, 11, 0), datetime(2025, 4, 19, 15, 45)],
        ),
        (
            "Jeudi 24 et vendredi 25 avril 2025",
            [date(2025, 4, 24), date(2025, 4, 25)],
        ),
        (
            "Samedi 3 et dimanche 4 mai\n 9h45, 11h, 15h30, 17h",
            [
                datetime(2025, 5, 3, 9, 45),
                datetime(2025, 5, 3, 11, 0),
                datetime(2025, 5, 3, 15, 30),
                datetime(2025, 5, 3, 17, 0),
                datetime(2025, 5, 4, 9, 45),
                datetime(2025, 5, 4, 11, 0),
                datetime(2025, 5, 4, 15, 30),
                datetime(2025, 5, 4, 17, 0),
            ],
        ),
        (
            "Mardi 13 mai 2025 de 9h30 à 17h30",
            [(datetime(2025, 5, 13, 9, 30), datetime(2025, 5, 13, 17, 30))],
        ),
        ("Le samedi 24 mai 2025", [date(2025, 5, 24)]),
    ]:
        result = parse_dates(txt, debug=debug, context=date(2025, 4, 24))
        assert result == dts


def test_mediatheque():
    result = parse_dates("23 Juil. 2025\n 13:00 - 15:00", debug=debug)
    assert result == [
        (datetime(2025, 7, 23, 13, 00), datetime(2025, 7, 23, 15, 00))
    ]
