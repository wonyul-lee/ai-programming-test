import pytest

from load_scores import load_scores


def test_load_scores_keeps_valid_rows_and_duplicate_names(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "\ufeffname,score\n"
        "  김하나  , 0 \n"
        '"최,네번",100\n'
        "김하나,88\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("김하나", 0), ("최,네번", 100), ("김하나", 88)]
    assert skipped == []


def test_load_scores_records_invalid_rows_and_ignores_blank_lines(tmp_path):
    csv_file = tmp_path / "invalid_scores.csv"
    csv_file.write_text(
        "name,score\n"
        "\n"
        "only-name\n"
        "too,many,columns\n"
        ",10\n"
        "no-score,\n"
        "not-an-integer,abc\n"
        "too-low,-1\n"
        "too-high,101\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == []
    assert skipped == [
        (3, "only-name", "열 개수가 2가 아님"),
        (4, "too,many,columns", "열 개수가 2가 아님"),
        (5, ",10", "이름이 비어 있음"),
        (6, "no-score,", "점수가 비어 있음"),
        (7, "not-an-integer,abc", "점수가 정수가 아님"),
        (8, "too-low,-1", "점수가 0~100 밖"),
        (9, "too-high,101", "점수가 0~100 밖"),
    ]


@pytest.mark.parametrize("contents", ["name,score\n", ""])
def test_load_scores_returns_empty_lists_when_there_are_no_data_rows(
    tmp_path, contents
):
    csv_file = tmp_path / "empty_scores.csv"
    csv_file.write_text(contents, encoding="utf-8")

    assert load_scores(csv_file) == ([], [])


def test_load_scores_raises_for_missing_file(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(missing_file)