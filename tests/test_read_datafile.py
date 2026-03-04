from pathlib import Path

from pypsucurvetrace.read_datafile import measurement_data


def test_get_t_returns_none_array_when_temperature_column_missing(tmp_path: Path):
    datafile = tmp_path / "no_temp.dat"
    datafile.write_text(
        "\n".join(
            [
                "% header",
                "0 0 1.0 0.1 0 2.0 0 0 0 0",
                "1 1 1.2 0.2 0 2.2 0 0 0 0",
            ]
        )
    )

    data = measurement_data(str(datafile))
    temps = data.get_T(exclude_CC=True)

    assert len(temps) == 2
    assert all(t is None for t in temps)
