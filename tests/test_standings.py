from league_table.models import Match, TeamRecord
from league_table.standings import build_standings, sort_standings


def test_win_draw_loss_points():
    matches = [
        Match("1974-08-17", "A", "B", 2, 1),  # A win
        Match("1974-08-24", "B", "A", 1, 1),  # draw
        Match("1974-08-31", "C", "A", 3, 0),  # A loss
    ]
    table = {r.team: r for r in build_standings(matches)}

    a = table["A"]
    assert (a.played, a.won, a.drawn, a.lost) == (3, 1, 1, 1)
    assert a.points == 2 + 1 + 0
    assert (a.goals_for, a.goals_against) == (3, 5)

    b = table["B"]
    assert (b.played, b.won, b.drawn, b.lost) == (2, 0, 1, 1)
    assert b.points == 0 + 1

    c = table["C"]
    assert (c.played, c.won, c.drawn, c.lost) == (1, 1, 0, 0)
    assert c.points == 2


def test_sort_by_points_then_goal_average():
    # Equal points (both 6 from 3 games), but X has a better goal average.
    records = [
        TeamRecord(team="X", played=3, won=3, drawn=0, lost=0, goals_for=6, goals_against=3, points=6),
        TeamRecord(team="Y", played=3, won=3, drawn=0, lost=0, goals_for=6, goals_against=2, points=6),
    ]
    ordered = sort_standings(records)
    assert [r.team for r in ordered] == ["Y", "X"]  # Y: 3.0 avg beats X: 2.0 avg


def test_sort_falls_back_to_goals_for_then_name():
    records = [
        TeamRecord(team="Zebra", played=1, points=3, goals_for=2, goals_against=1),
        TeamRecord(team="Alpha", played=1, points=3, goals_for=2, goals_against=1),
        TeamRecord(team="Beta", played=1, points=3, goals_for=3, goals_against=1),
    ]
    ordered = sort_standings(records)
    # Beta has more goals for (same avg-tiebreak level as it's better anyway),
    # then Alpha before Zebra alphabetically since points/avg/GF are tied.
    assert [r.team for r in ordered] == ["Beta", "Alpha", "Zebra"]


def test_goal_average_zero_against_edge_cases():
    scored_and_conceded_none = TeamRecord(team="Scoreless", goals_for=0, goals_against=0)
    assert scored_and_conceded_none.goal_average == 1.0

    perfect_defense = TeamRecord(team="Perfect", goals_for=5, goals_against=0)
    assert perfect_defense.goal_average == 5.0
