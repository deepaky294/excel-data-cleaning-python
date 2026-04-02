import pandas as pd
import pytest

from data_loader import DataLoadError, list_files, load_dataframe


def test_load_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("a,b\n1,2\n3,4\n")

    df = load_dataframe(str(csv_path))

    assert df.shape == (2, 2)
    assert df["a"].tolist() == [1, 3]


def test_load_excel(tmp_path):
    excel_path = tmp_path / "sample.xlsx"
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_excel(excel_path, index=False)

    df = load_dataframe(str(excel_path))

    assert df.shape == (2, 2)
    assert df["b"].tolist() == [3, 4]


def test_unsupported_file_type(tmp_path):
    unsupported_path = tmp_path / "sample.txt"
    unsupported_path.write_text("hello world")

    with pytest.raises(DataLoadError):
        load_dataframe(str(unsupported_path))


def test_list_files(tmp_path):
    (tmp_path / "one.csv").write_text("x\n1\n")
    (tmp_path / "two.csv").write_text("x\n2\n")

    files = list_files(str(tmp_path), "*.csv")

    assert len(files) == 2
