import pytest

from load_scores import load_scores


def test_load_scores_keeps_valid_scores_and_duplicate_names(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "\ufeffname,score\n"
        "  민지 , 0 \n"
        '"최,윤",100\n'
        "민지,75\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("민지", 0), ("최,윤", 100), ("민지", 75)]
    assert skipped == []


def test_load_scores_records_invalid_rows_and_ignores_blank_lines(tmp_path):
    csv_file = tmp_path / "mixed_scores.csv"
    csv_file.write_text(
        "name,score\n"
        "\n"
        "한 칸만\n"
        "열,개수,초과\n"
        "   ,80\n"
        "지수,   \n"
        "서연,구십\n"
        "도윤,-1\n"
        "하늘,101\n"
        "유진,92\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("유진", 92)]
    assert skipped == [
        (3, "한 칸만", "열 개수가 2가 아님"),
        (4, "열,개수,초과", "열 개수가 2가 아님"),
        (5, "   ,80", "이름이 비어 있음"),
        (6, "지수,   ", "점수가 비어 있음"),
        (7, "서연,구십", "점수가 정수가 아님"),
        (8, "도윤,-1", "점수가 0~100 밖"),
        (9, "하늘,101", "점수가 0~100 밖"),
    ]


@pytest.mark.parametrize("contents", ["", "name,score\n"])
def test_load_scores_returns_empty_results_without_data_rows(tmp_path, contents):
    csv_file = tmp_path / "empty_scores.csv"
    csv_file.write_text(contents, encoding="utf-8")

    assert load_scores(csv_file) == ([], [])


def test_load_scores_propagates_file_not_found_error(tmp_path):
    missing_file = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(missing_file)