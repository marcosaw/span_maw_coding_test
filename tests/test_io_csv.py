import io

import pytest

from league_table.io_csv import MatchParseError, read_matches, write_standings
from league_table.models import TeamRecord


def test_read_matches_parses_valid_rows():
    csv_text = (
        "Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\n"
        "1974-08-17,Ipswich Town,Manchester City,2,1\n"
        "1974-08-17,Arsenal,Leeds United,1,1\n"
    )
    matches = read_matches(io.StringIO(csv_text))
    assert len(matches) == 2
    assert matches[0].home_team == "Ipswich Town"
    assert matches[0].away_team == "Manchester City"
    assert matches[0].home_goals == 2
    assert matches[0].away_goals == 1
    assert matches[1].home_goals == matches[1].away_goals == 1


def test_read_matches_skips_blank_lines():
    csv_text = (
        "Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\n"
        "1974-08-17,Ipswich Town,Manchester City,2,1\n"
        "\n"
        "1974-08-24,Arsenal,Leeds United,1,1\n"
    )
    matches = read_matches(io.StringIO(csv_text))
    assert len(matches) == 2


def test_read_matches_rejects_missing_header():
    csv_text = "HomeTeam,AwayTeam,HomeGoals,AwayGoals\nA,B,1,0\n"
    with pytest.raises(MatchParseError, match="missing required column"):
        read_matches(io.StringIO(csv_text))


def test_read_matches_rejects_empty_file():
    with pytest.raises(MatchParseError, match="empty"):
        read_matches(io.StringIO(""))


@pytest.mark.parametrize(
    "bad_value",
    ["", "two", "1.5", "-1"],
)
def test_read_matches_rejects_bad_goal_values(bad_value):
    csv_text = f"Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\n1974-08-17,A,B,{bad_value},1\n"
    with pytest.raises(MatchParseError):
        read_matches(io.StringIO(csv_text))


def test_read_matches_rejects_team_playing_itself():
    csv_text = "Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\n1974-08-17,A,A,1,1\n"
    with pytest.raises(MatchParseError, match="cannot play itself"):
        read_matches(io.StringIO(csv_text))


def test_read_matches_error_message_includes_line_number():
    csv_text = (
        "Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\n"
        "1974-08-17,A,B,1,1\n"
        "1974-08-24,C,D,x,1\n"
    )
    with pytest.raises(MatchParseError, match="line 3"):
        read_matches(io.StringIO(csv_text))


def test_write_standings_format():
    record = TeamRecord(
        team="Ipswich Town",
        played=10,
        won=8,
        drawn=1,
        lost=1,
        goals_for=24,
        goals_against=10,
        points=17,
    )
    out = io.StringIO()
    write_standings([record], out)
    lines = out.getvalue().splitlines()
    assert lines[0] == "Pos,Team,P,W,D,L,F,A,GAvg,Pts"
    assert lines[1] == "1,Ipswich Town,10,8,1,1,24,10,2.400,17"
