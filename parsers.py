from functools import partial
from typing import Any, Callable
import re

polish_letters_lower = "ąćęłńóśźż"
polish_letters_upper = polish_letters_lower.upper()
polish_letters_all = polish_letters_lower + polish_letters_upper


def _extract_and_cast(
    line: str, pattern: str, keys: list[str], cast: list[Any], default: list[Any]
) -> dict[str, Any]:
    try:
        values = re.search(pattern, line).groups()
        values = [
            value if cast[i] is None else cast[i](value)
            for i, value in enumerate(values)
        ]
        values = [
            value if value != "" else default[i] for i, value in enumerate(values)
        ]
    except AttributeError:
        print(line)
        raise Exception("Invalid line format")
    return dict(zip(keys, values))


class ZTMParserWK:
    def __init__(self, data: list[str]) -> None:
        self.data = data

    def __call__(self) -> list[dict[str, Any]]:
        # a) unikalny identyfikator kursu,
        # b) unikalny sześciocyfrowy numer przystanku,
        # c) oznaczenie typu dnia kursowania,
        # d) godzinę odjazdu z przystanku lub przyjazdu na przystanek końcowy,
        # e) dodatkowy atrybut kursu.
        out = []
        keys = ["course_id", "stop_id", "day_type", "time", "extra"]
        cast = [None, None, None, None, None]
        default = [None, None, None, None, None]
        pattern = r"^([\w\-\/\.\_]+)\s{2}(\d+)\s{1}(\w+)\s{1,2}(\d{1,2}\.?\d{0,2})\s{0,2}(.*)?"
        for line in self.data:
            parsed_line = _extract_and_cast(line, pattern, keys, cast, default)
            out.append(parsed_line)

        return out


class ZTMParserPR:
    def __init__(self, data: list[str]) -> None:
        self.data = data

    def __call__(self) -> list[dict[str, Any]]:
        # - unikalny sześciocyfrowy numer przystanku,
        # - liczba pozycji - wykazów linii,
        # - ulica, na której położony jest przystanek,
        # - kierunek zbiorczy dla przystanku,
        # - współrzędne GPS określające położenie przystanku.
        out = []
        keys_common = [
            "id",
            "group_id",
            "station_id",
            "source",
            "target",
            "longitude",
            "latitude",
            "pu",
        ]

        # source/target may be * if street name is not available
        def cast_to_none(
            value: str,
            none_values: list[str] = ["*" * 30, ""],
            default_cast: Callable | None = None,
        ) -> Any | None:
            if value in none_values:
                return None
            else:
                return value if default_cast is None else default_cast(value)

        cast_common = [
            int,
            int,
            int,
            cast_to_none,
            cast_to_none,
            None,
            None,
            partial(cast_to_none, none_values=["?", ""], default_cast=int),
        ]
        default_common = [None] * len(keys_common)
        pattern_common = r"^((\d{4})(\d{2}))\s+\d+\s+Ul\.\/Pl\.:\s+(.*?),?\s+Kier\.:\s+(.*?),?\s+Y\s*=\s*([\d\.y]+)\s+X\s*=\s*([\d\.x]+)\s+Pu\s*=\s*([\d\?]+)$"
        keys = ["number_of_lines", "stop_type", "lines_list"]

        def cast_to_list(value: str, separator: str = r"\s{2,}") -> list[str]:
            return re.split(separator, value)

        cast = [int, None, cast_to_list]
        default = [None] * len(keys)
        pattern = r"^L\s+(\d+)\s+\-\s+(.*):\s+(.*)$"
        for line in self.data:
            # values = line.split("  ")
            if not line.startswith("L"):
                parsed_common = _extract_and_cast(
                    line, pattern_common, keys_common, cast_common, default_common
                )
            else:
                parsed_line = _extract_and_cast(line, pattern, keys, cast, default)

                out.append({**parsed_common, **parsed_line})

        return out


class ZTMParserZP:
    def __init__(self, data: list[str]) -> None:
        self.data = data

    def __call__(self) -> list[dict[str, Any]]:
        # - czterocyfrowy unikalny numer zespołu przystankowego,
        # - nazwę zespołu przystankowego,
        # - dwuznakowy symbol miejscowości,
        # - nazwę miejscowości
        out = []
        keys = ["group_id", "group_name", "city_symbol", "city_name"]
        cast = [int, None, None, None]
        default = [None] * len(keys)
        pattern = (
            rf"^(\d{{4}})\s+(.*?),?\s+([A-Z{polish_letters_upper}\d\-]{{2}})\s+(.*?)$"
        )
        skip_flg = 0
        for line in self.data:
            if line.startswith("*"):
                skip_flg = 1
                continue
            if skip_flg == 1:
                if line.startswith("#"):
                    skip_flg = 0
                continue
            parsed_line = _extract_and_cast(line, pattern, keys, cast, default)
            out.append(parsed_line)

        return out
