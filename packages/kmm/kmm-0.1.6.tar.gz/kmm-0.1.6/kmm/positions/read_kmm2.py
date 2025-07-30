import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import validate_arguments

pattern = re.compile(r".+\[.+\]")
pattern2 = re.compile(r"CMAST")

expected_columns = [
    "code",
    "centimeter",
    "track_section",
    "kilometer",
    "meter",
    "track_lane",
    "1?",
    "2?",
    "3?",
    "4?",
    "northing",
    "easting",
    "contact_wire_material",
    "rail_model",
    "sliper_model",
    "between_stations",
    "5?",
    "6?",
    "7?",
    "8?",
    "max_speed",
    "datetime",
    "bearing",
    "linear_coordinate",
]
expected_dtypes = dict(
    centimeter=np.int64,
    track_section=str,
    kilometer=np.int32,
    meter=np.int32,
    track_lane=str,
    northing=np.float32,
    easting=np.float32,
)


@validate_arguments
def read_kmm2(
    path: Path, raise_on_malformed_data: bool = True, replace_commas: bool = True
):
    skiprows = [
        index
        for index, line in enumerate(path.read_text(encoding="latin1").splitlines())
        if pattern.match(line) or pattern2.match(line)
    ]
    with open(path, "r", encoding="latin1") as f:
        line = f.readline()
        if line.startswith("VER"):
            skiprows = [0] + skiprows
        elif raise_on_malformed_data and not line.startswith("POS"):
            raise ValueError("Malformed data, first line is not POS or VER")

    try:
        if replace_commas:
            with open(path, "r", encoding="latin1") as f:
                content = f.read()
            content = content.replace(",", ".")
            file_obj = StringIO(content)
        else:
            file_obj = path

        try:
            df = pd.read_csv(
                file_obj,
                skiprows=skiprows,
                delimiter="\t",
                encoding="latin1" if not replace_commas else None,
                low_memory=False,
                header=None,
            )
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=expected_columns)
        else:
            return with_column_names(df)
    except Exception as e:
        raise ValueError("Unable to parse kmm2 file, invalid csv.") from e


def with_column_names(df):
    length_diff = len(df.columns) - len(expected_columns)
    if length_diff > 0:
        columns = expected_columns + [f"{i}?" for i in range(8, 8 + length_diff)]
    elif length_diff < 0:
        columns = expected_columns[:length_diff]
    else:
        columns = expected_columns
    df.columns = columns
    df.astype(
        {
            column: dtype
            for column, dtype in expected_dtypes.items()
            if column in df.columns
        }
    )
    return df


def test_patterns():
    assert pattern.match("Västerås central [Vå]")
    assert pattern2.match("CMAST   281-2B")


def test_extra_columns():
    read_kmm2(Path("tests/extra_columns.kmm2"))
