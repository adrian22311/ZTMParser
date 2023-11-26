from __future__ import annotations
from typing import Iterator, Callable, Any
import parsers


class ZTMLazyReaderException(Exception):
    pass


class ZTMLazyReader:
    def __init__(
        self,
        path: str,
        encoding: str = "windows-1250",
        start_tag: str = "*",
        end_tag: str = "#",
    ):
        self.path = path
        self.encoding = encoding
        self.start_tag = start_tag
        self.end_tag = end_tag

    def __iter__(self) -> Iterator[str]:
        with open(self.path, encoding=self.encoding) as f:
            for line in f:
                yield line.strip()

    def __next__(self) -> str:
        return next(self.__iter__())

    def is_start_tag(self, line: str) -> bool:
        return line.startswith(self.start_tag)

    def is_end_tag(self, line: str) -> bool:
        return line.startswith(self.end_tag)

    def get_tag_length(self, line: str) -> tuple[str, int]:
        assert self.is_start_tag(line), "Line is not a start tag"
        try:
            lines = line.split(" ")
            if len(lines) > 1:
                tag, *_, length = lines
                tag = tag[1:]
                length = int(length)
            else:
                tag = lines[0][1:]
                length = 1
        except ValueError:
            raise ZTMLazyReaderException("Invalid tag format")
        return tag, length


class ZTMParserNotImplementedException(Exception):
    pass


class ZTMTagReaderException(Exception):
    pass


class ZTMTagReader:
    def __init__(
        self,
        path: str,
        encoding: str = "windows-1250",
        start_tag: str = "*",
        end_tag: str = "#",
    ):
        self.path = path
        self.encoding = encoding
        self.start_tag = start_tag
        self.end_tag = end_tag

    def read(self, tag: str) -> list[str]:
        reader = ZTMLazyReader(self.path, self.encoding, self.start_tag, self.end_tag)

        out = []
        keep_reading = False
        for line in reader:
            if reader.is_start_tag(line):
                _tag, _ = reader.get_tag_length(line)
                if _tag == tag:
                    keep_reading = True
                    continue
            if reader.is_end_tag(line):
                if line[1:] == tag:
                    keep_reading = False
            if keep_reading:
                out.append(line)
        return out


class ZTMParser:
    def __init__(self, tag: str):
        self.tag = tag

    def __call__(self, data: list[str]) -> Callable[[list[str]], list[dict[str, Any]]]:
        def not_implemented(tag: str) -> callable:
            def _not_implemented(_) -> None:
                raise ZTMParserNotImplementedException(
                    f"Parser for {tag} tag wasn't implemented"
                )

            return _not_implemented

        parser = getattr(parsers, f"ZTMParser{self.tag}", not_implemented(self.tag))(
            data
        )
        return parser
