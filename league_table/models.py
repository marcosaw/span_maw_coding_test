"""Core data types for match results and team standings."""

from dataclasses import dataclass

POINTS_WIN = 2
POINTS_DRAW = 1
POINTS_LOSS = 0


@dataclass(frozen=True)
class Match:
    date: str
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int


@dataclass
class TeamRecord:
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @property
    def goal_average(self) -> float:
        # Goal average (F/A), not goal difference: the Football League's tie-break
        # rule until the 1976/77 season, so it's the period-accurate metric here.
        # Division by zero has no historical convention with a real match dataset,
        # so we fall back to goals scored (or a neutral 1.0 for a scoreless team).
        if self.goals_against > 0:
            return self.goals_for / self.goals_against
        if self.goals_for > 0:
            return float(self.goals_for)
        return 1.0

    def record_result(self, goals_for: int, goals_against: int) -> None:
        self.played += 1
        self.goals_for += goals_for
        self.goals_against += goals_against
        if goals_for > goals_against:
            self.won += 1
            self.points += POINTS_WIN
        elif goals_for < goals_against:
            self.lost += 1
            self.points += POINTS_LOSS
        else:
            self.drawn += 1
            self.points += POINTS_DRAW
