import pandas as pd
import pytest
from src.utils import generate_row_hash, retry_with_backoff, rotate_file_backup


# --- generate_row_hash tests ---
def test_generate_row_hash_normal():
    row = pd.Series(
        {
            "code": "1234",
            "name": "TestStock",
            "per": 10.5,
            "pbr": 1.2,
            "roe": 8.0,
            "dividend_yield": 2.5,
            "current_ratio": 150.0,
            "rsi": 50.0,
            "quant_score": 80.0,
        }
    )
    hash1 = generate_row_hash(row)
    hash2 = generate_row_hash(row)
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) == 32


def test_generate_row_hash_with_nan():
    row = pd.Series({"code": "1234", "name": "TestStock", "per": float("nan")})
    hash_val = generate_row_hash(row)
    assert isinstance(hash_val, str)


def test_generate_row_hash_int_float():
    row1 = pd.Series({"code": "111", "per": 10.0})  # float ending in .0
    row2 = pd.Series({"code": "111", "per": 10})  # int

    # Logic in utils.py converts integer-floats to int str: "10.0" -> "10"
    # So these should generate same hash
    assert generate_row_hash(row1) == generate_row_hash(row2)


# --- retry_with_backoff tests ---
def test_retry_success():
    counter = 0

    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def succes_on_second_try():
        nonlocal counter
        counter += 1
        if counter < 2:
            raise ValueError("Fail once")
        return "Success"

    assert succes_on_second_try() == "Success"
    assert counter == 2


def test_retry_failure():
    counter = 0

    @retry_with_backoff(max_retries=2, base_delay=0.01)
    def always_fail():
        nonlocal counter
        counter += 1
        raise ValueError("Fail always")

    with pytest.raises(ValueError):
        always_fail()
    assert counter == 3  # Initial + 2 retries


# --- rotate_file_backup tests ---
def test_rotate_file_backup_no_file(tmp_path):
    # Should just return without error
    target = tmp_path / "non_existent.txt"
    rotate_file_backup(str(target))
    assert not target.exists()


def test_rotate_file_backup_exists(tmp_path):
    target = tmp_path / "test.txt"
    target.write_text("content")

    rotate_file_backup(str(target))

    assert not target.exists()  # Should be moved
    backups = list(tmp_path.glob("test_*.txt"))
    assert len(backups) == 1
    assert backups[0].read_text() == "content"


def test_rotate_file_backup_collision(tmp_path):
    target = tmp_path / "data.txt"
    target.write_text("v1")

    # Mock datetime to return fixed string to cause collision if counter logic wasn't there
    # But utils.py uses internal counter loop.
    # Just running twice should produce two backup files

    rotate_file_backup(str(target))  # Backup v1

    target.write_text("v2")
    rotate_file_backup(str(target))  # Backup v2

    backups = sorted(list(tmp_path.glob("data_*.txt")))
    assert len(backups) == 2
