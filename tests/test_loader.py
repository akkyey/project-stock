import os
import sys

import numpy as np
import pytest

# Adjust path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.loader import clean_number, load_csv


def test_clean_number():
    assert clean_number("123") == 123.0
    assert clean_number("1,234.56") == 1234.56
    assert clean_number("12.5%") == 12.5
    assert np.isnan(clean_number("abc"))
    assert clean_number(123) == 123
    assert clean_number(None) is None


def test_load_csv_utf8(tmp_path):
    file_path = tmp_path / "test_utf8.csv"
    # Create UTF-8 CSV with quoted fields for commas
    content = 'コード,銘柄名,現在値,PER(株価収益率)\n7203,トヨタ,"2,000",10.5'
    file_path.write_text(content, encoding="utf-8")

    df = load_csv(str(file_path))

    assert "code" in df.columns
    assert "name" in df.columns
    assert "current_price" in df.columns
    assert "per" in df.columns

    assert df.iloc[0]["code"] == "7203"
    assert df.iloc[0]["current_price"] == 2000.0
    assert df.iloc[0]["per"] == 10.5


def test_load_csv_shift_jis(tmp_path):
    file_path = tmp_path / "test_sjis.csv"
    # Create Shift-JIS CSV with quoted fields for commas
    content = 'コード,銘柄名,現在値\n9984,ソフトバンク,"5,000"'
    with open(file_path, "w", encoding="shift_jis") as f:
        f.write(content)

    df = load_csv(str(file_path))

    assert df.iloc[0]["code"] == "9984"
    assert df.iloc[0]["current_price"] == 5000.0


def test_load_csv_file_not_found(tmp_path):
    non_existent_file = str(tmp_path / "non_existent.csv")
    with pytest.raises(Exception):
        load_csv(non_existent_file)


def test_load_csv_code_cleaning(tmp_path):
    file_path = tmp_path / "test_code.csv"
    # Code as float string
    content = "コード\n7203.0"
    file_path.write_text(content, encoding="utf-8")

    df = load_csv(str(file_path))
    assert df.iloc[0]["code"] == "7203"  # .0 removed
