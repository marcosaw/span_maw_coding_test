import io

from league_table.cli import main

SAMPLE_CSV = (
    "Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\n"
    "1974-08-17,Ipswich Town,Manchester City,2,1\n"
    "1974-08-17,Arsenal,Leeds United,1,1\n"
    "1974-08-24,Manchester City,Arsenal,3,0\n"
)

EXPECTED_STANDINGS = (
    "Pos,Team,P,W,D,L,F,A,GAvg,Pts\n"
    "1,Manchester City,2,1,0,1,4,2,2.000,2\n"
    "2,Ipswich Town,1,1,0,0,2,1,2.000,2\n"
    "3,Leeds United,1,0,1,0,1,1,1.000,1\n"
    "4,Arsenal,2,0,1,1,1,4,0.250,1\n"
)


def test_file_to_file(tmp_path):
    input_path = tmp_path / "matches.csv"
    output_path = tmp_path / "standings.csv"
    input_path.write_text(SAMPLE_CSV, encoding="utf-8")

    exit_code = main([str(input_path), "-o", str(output_path)])

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == EXPECTED_STANDINGS


def test_stdin_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(SAMPLE_CSV))

    exit_code = main([])

    assert exit_code == 0
    assert capsys.readouterr().out == EXPECTED_STANDINGS


def test_file_to_stdout(tmp_path, capsys):
    input_path = tmp_path / "matches.csv"
    input_path.write_text(SAMPLE_CSV, encoding="utf-8")

    exit_code = main([str(input_path)])

    assert exit_code == 0
    assert capsys.readouterr().out == EXPECTED_STANDINGS


def test_missing_input_file_reports_error(capsys):
    exit_code = main(["does-not-exist.csv"])

    assert exit_code == 1
    assert "not found" in capsys.readouterr().err


def test_malformed_csv_reports_error(tmp_path, capsys):
    input_path = tmp_path / "matches.csv"
    input_path.write_text("Date,HomeTeam,AwayTeam,HomeGoals,AwayGoals\nx,A,B,oops,1\n", encoding="utf-8")

    exit_code = main([str(input_path)])

    assert exit_code == 1
    assert "line 2" in capsys.readouterr().err
