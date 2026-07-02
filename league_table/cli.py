"""Command-line entry point: CSV match results in, CSV standings table out."""

import argparse
import sys
from contextlib import contextmanager
from typing import Iterator, Sequence, TextIO

from .io_csv import MatchParseError, read_matches, write_standings
from .standings import build_standings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="league-table",
        description=(
            "Compute a football league standings table (2 pts win / 1 pt draw) "
            "from a CSV file of match results."
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="input CSV file of match results (default: read from stdin, or pass '-')",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="output CSV file for the standings table (default: write to stdout, or pass '-')",
    )
    return parser


@contextmanager
def _open_input(path: str) -> Iterator[TextIO]:
    if path == "-":
        yield sys.stdin
        return
    with open(path, "r", newline="", encoding="utf-8") as f:
        yield f


@contextmanager
def _open_output(path: str) -> Iterator[TextIO]:
    if path == "-":
        yield sys.stdout
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        yield f


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        with _open_input(args.input) as infile:
            matches = read_matches(infile)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1
    except MatchParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    standings = build_standings(matches)

    with _open_output(args.output) as outfile:
        write_standings(standings, outfile)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
