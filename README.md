# league-table

A command-line tool that turns a CSV of football match results into a CSV league
standings table, using the classic English **2 points for a win, 1 for a draw**
scoring system.

The bundled example is the **English First Division, 1974/75 season, standings
after Week 10**.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `league-table` console script. No third-party runtime
dependencies are required — the tool only uses the Python standard library.

## Usage

Input can come from a filename argument or stdin; output can go to a filename
argument (`-o/--output`) or stdout. Omit either, or pass `-`, to use stdio.

```bash
# file -> file
league-table examples/matches_1974_75_week10.csv -o standings.csv

# file -> stdout
league-table examples/matches_1974_75_week10.csv

# stdin -> stdout
cat examples/matches_1974_75_week10.csv | league-table

# stdin -> file
league-table - -o standings.csv < examples/matches_1974_75_week10.csv
```

Equivalently, without installing: `python -m league_table ...` from the repo root.

Malformed input (missing header columns, non-numeric or negative goals, a team
"playing itself", etc.) is rejected with an error on stderr naming the offending
line number, and the process exits with status 1.

## CSV formats

### Input — one match result per row

```
Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals
1974-08-17,Ipswich Town,Manchester City,2,1
```

| Column | Meaning |
|---|---|
| `Date` | `YYYY-MM-DD`. Kept for readability/traceability; not used in the calculation. |
| `HomeTeam` / `AwayTeam` | Club names (must differ). |
| `HomeGoals` / `AwayGoals` | Non-negative integers. |

The tool aggregates *every* match row it's given — there's no round/week filter.
"Standings after Week 10" is expressed by which matches the input file contains
(the first 10 matchweeks), not by a runtime flag.

### Output — conventional English league table format

```
Pos,Team,P,W,D,L,F,A,GAvg,Pts
1,Ipswich Town,10,8,1,1,18,6,3.000,17
```

| Column | Meaning |
|---|---|
| `Pos` | 1-based rank after sorting. |
| `P/W/D/L` | Played / Won / Drawn / Lost. |
| `F/A` | Goals For / Against. |
| `GAvg` | Goal average (F ÷ A, 3 dp) — see note below. |
| `Pts` | 2 per win, 1 per draw. |

Sort order is cascading and fully deterministic, so there are never shared "3="
ranks: **Points → Goal Average → Goals For → Team name**.

**Why goal average, not goal difference:** the Football League used goal average
(F ÷ A) to separate teams level on points from 1894/95 until the end of 1975/76;
goal difference wasn't adopted until the 1976/77 season. Since this table is
dated 1974/75, goal average is the period-accurate tie-break — goal difference
would be an anachronism here. (A team with 0 goals against sorts by goals scored
instead of a division-by-zero average; a team with 0 for and 0 against gets a
neutral average of `1.000`. See `TeamRecord.goal_average` in `models.py`.)

## Example data

`examples/matches_1974_75_week10.csv` uses the real 22 clubs of the 1974/75
First Division. A reliably sourced, dated, round-by-round fixture list for
those first 10 matchweeks isn't available online (Wikipedia's season article
has only a final results grid, no per-round dates), so rather than invent 110
scorelines and present them as scraped history, the fixtures are **illustrative**
— constructed to honor the two verifiable facts about the real table at that
point in the season:

- Ipswich Town led the table after 10 games, with 8 wins, 2 points clear of
  Manchester City.
- Queens Park Rangers, Tottenham Hotspur, Arsenal and Leeds United were level
  on points at the bottom.

`examples/standings_1974_75_week10.csv` is the program's own output for that
input — regenerate it any time with:

```bash
league-table examples/matches_1974_75_week10.csv -o examples/standings_1974_75_week10.csv
```

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```
