import pandas as pd
from backtest.batch.io import OutputWriter


def test_output_writer_writes_matches(tmp_path):
    writer = OutputWriter(tmp_path)
    day = "2025-03-07"
    rows = [("AAA", "F1"), ("AAA", "F2"), ("BBB", "F3")]
    csv_path = writer.write_day(day, rows)
    df = pd.read_csv(csv_path)
    expected = pd.DataFrame(
        [
            ["2025-03-07", "AAA", "F1"],
            ["2025-03-07", "AAA", "F2"],
            ["2025-03-07", "BBB", "F3"],
        ],
        columns=["date", "symbol", "filter_code"],
    )
    pd.testing.assert_frame_equal(df, expected)
