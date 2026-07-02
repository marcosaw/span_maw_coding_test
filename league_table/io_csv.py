"""Reading match results from CSV and writing the standings table back out."""

import csv
from typing import Iterable, TextIO

from .models import Match, TeamRecord

REQUIRED_INPUT_FIELDS = ["Date", "HomeTeam", "AwayTeam", "HomeGoals", "AwayGoals"]
OUTPUT_FIELDS = ["Pos", "Team", "P", "W", "D", "L", "F", "A", "GAvg", "Pts"]


class MatchParseError(ValueError):
    """Raised when a row of the input CSV cannot be parsed as a match result."""


def _parse_goals(raw: str, field_name: str, line_no: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise MatchParseError(
            f"line {line_no}: {field_name!r} must be a whole number, got {raw!r}"
        ) from None
    if value < 0:
        raise MatchParseError(f"line {line_no}: {field_name!r} cannot be negative, got {value}")
    return value


def read_matches(fileobj: TextIO) -> list[Match]:
    reader = csv.DictReader(fileobj)
    if reader.fieldnames is None:
        raise MatchParseError("input CSV is empty; expected a header row")
    missing = [f for f in REQUIRED_INPUT_FIELDS if f not in reader.fieldnames]
    if missing:
        raise MatchParseError(
            f"input CSV header is missing required column(s): {', '.join(missing)}"
        )

    matches: list[Match] = []
    for line_no, row in enumerate(reader, start=2):  # header is line 1
        if all((value is None or value.strip() == "") for value in row.values()):
            continue  # skip blank lines

        home_team = (row["HomeTeam"] or "").strip()
        away_team = (row["AwayTeam"] or "").strip()
        if not home_team or not away_team:
            raise MatchParseError(f"line {line_no}: HomeTeam and AwayTeam are required")
        if home_team == away_team:
            raise MatchParseError(f"line {line_no}: a team cannot play itself ({home_team!r})")

        home_goals = _parse_goals(row["HomeGoals"], "HomeGoals", line_no)
        away_goals = _parse_goals(row["AwayGoals"], "AwayGoals", line_no)

        matches.append(
            Match(
                date=(row["Date"] or "").strip(),
                home_team=home_team,
                away_team=away_team,
                home_goals=home_goals,
                away_goals=away_goals,
            )
        )
    return matches


def write_standings(records: Iterable[TeamRecord], fileobj: TextIO) -> None:
    writer = csv.writer(fileobj, lineterminator="\n")
    writer.writerow(OUTPUT_FIELDS)
    for pos, record in enumerate(records, start=1):
        writer.writerow(
            [
                pos,
                record.team,
                record.played,
                record.won,
                record.drawn,
                record.lost,
                record.goals_for,
                record.goals_against,
                f"{record.goal_average:.3f}",
                record.points,
            ]
        )
