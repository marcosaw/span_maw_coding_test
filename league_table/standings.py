"""Aggregating match results into a sorted league standings table."""

from .models import Match, TeamRecord


def build_standings(matches: list[Match]) -> list[TeamRecord]:
    records: dict[str, TeamRecord] = {}

    def record_for(team: str) -> TeamRecord:
        if team not in records:
            records[team] = TeamRecord(team=team)
        return records[team]

    for match in matches:
        record_for(match.home_team).record_result(match.home_goals, match.away_goals)
        record_for(match.away_team).record_result(match.away_goals, match.home_goals)

    return sort_standings(list(records.values()))


def sort_standings(records: list[TeamRecord]) -> list[TeamRecord]:
    # Cascading, fully deterministic order: Points -> Goal Average -> Goals For ->
    # Team name. Goal average (not goal difference) is the period-accurate
    # tie-break for a 1974/75 table; see league_table.models.TeamRecord.goal_average.
    return sorted(
        records,
        key=lambda r: (-r.points, -r.goal_average, -r.goals_for, r.team),
    )
