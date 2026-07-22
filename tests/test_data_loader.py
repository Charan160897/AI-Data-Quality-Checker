from io import StringIO

from src.data_loader import load_csv


def test_load_valid_csv():
    csv_file = StringIO("Name,Age\nJohn,25\nAmy,30")

    result = load_csv(csv_file)

    assert result is not None
    assert result.shape == (2, 2)


def test_load_empty_csv():
    csv_file = StringIO("Name,Age\n")

    result = load_csv(csv_file)

    assert result == "EMPTY"