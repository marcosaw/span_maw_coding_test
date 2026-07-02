# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A CLI tool (`league-table`) that reads football match results from a CSV file and
writes a league standings table as CSV, scored with the historical English system
(2 points for a win, 1 for a draw, 0 for a loss). Pure Python standard library —
no runtime dependencies. The bundled example models the English First Division,
1974/75 season, standings after Week 10.

## Commands

```bash
# Setup (once)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run
league-table examples/matches_1974_75_week10.csv -o standings.csv   # file -> file
league-table examples/matches_1974_75_week10.csv                     # file -> stdout
cat examples/matches_1974_75_week10.csv | league-table               # stdin -> stdout
python -m league_table ...                                           # without installing

# Tests
pytest -q                        # full suite
pytest tests/test_standings.py   # one file
pytest -k goal_average           # by name
```

## Architecture

Data flows in one direction through four modules in `league_table/`:

```
io_csv.read_matches()  ->  list[Match]  ->  standings.build_standings()  ->  list[TeamRecord] (sorted)  ->  io_csv.write_standings()
```

- **`models.py`** — `Match` (one parsed row) and `TeamRecord` (one team's aggregated
  stats) dataclasses. `TeamRecord.record_result()` applies the win/draw/loss point
  rule; `TeamRecord.goal_average` computes the sort metric (see below).
- **`io_csv.py`** — all CSV parsing/formatting and validation. `read_matches` raises
  `MatchParseError` (with a 1-based line number) for bad rows — missing columns,
  non-numeric/negative goals, a team "playing itself", etc. `write_standings` owns
  the output column order/formatting (`OUTPUT_FIELDS`).
- **`standings.py`** — `build_standings` aggregates a flat match list into one
  `TeamRecord` per team (keyed by team name, first-seen order), then sorts via
  `sort_standings`.
- **`cli.py`** — argparse wiring and the stdin/stdout-vs-file plumbing (`-` or an
  omitted arg means stdio). `main(argv)` returns an exit code rather than calling
  `sys.exit` directly, which is what makes it easy to test (see `tests/test_cli.py`,
  which drives `main()` directly with `capsys`/`monkeypatch` instead of subprocess).

### Sort order — goal average, not goal difference

Standings sort cascades: **Points → Goal Average (F÷A) → Goals For → Team name**
(`standings.sort_standings`), which is fully deterministic — there are never tied
positions. Goal average, not goal difference, is used deliberately: the Football
League only switched to goal difference starting in the 1976/77 season, so for a
1974/75 table goal average is the period-accurate metric. Don't "fix" this to goal
difference. The zero-goals-against edge case is documented in
`TeamRecord.goal_average`.

### Input/output CSV contracts

Input requires an exact header `Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals`
(`io_csv.REQUIRED_INPUT_FIELDS`); output is
`Pos,Team,P,W,D,L,F,A,GAvg,Pts` (`io_csv.OUTPUT_FIELDS`). The tool has no
round/week filter — it aggregates every row in the input file, so "standings after
Week 10" is expressed by curating which matches are in the input file, not by a
runtime flag. See `README.md` for the full column-by-column format spec.

### Example data is illustrative, not scraped history

`examples/matches_1974_75_week10.csv` uses the real 22 1974/75 First Division
clubs, but a reliably sourced, dated, round-by-round fixture list for that season
isn't available, so the scorelines are constructed rather than historical record.
They do honor the two verifiable facts about the real table at that point in the
season (Ipswich Town led with 8 wins, 2 points clear of Manchester City; QPR,
Tottenham, Arsenal and Leeds United were level on points at the bottom) — don't
change these fixtures in a way that breaks those two invariants.
`examples/standings_1974_75_week10.csv` is the program's own output for that
input; regenerate it with the command in the README rather than hand-editing it.
