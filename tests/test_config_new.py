import tempfile, textwrap
from pathlib import Path
import pytest

from backtest.config import load_config, RootCfg

def _write_cfg(text: str) -> Path:
    tmp = tempfile.NamedTemporaryFile('w+', delete=False)
    tmp.write(text)
    tmp.flush()
    return Path(tmp.name)

def test_load_config_independent_defaults():
    cfg_text = textwrap.dedent(
        """
        project:
          out_dir: out
          run_mode: range
          start_date: '2020-01-01'
          end_date: '2020-12-31'
        data:
          excel_dir: data
          filters_csv: filters.csv
        """
    )
    path = _write_cfg(cfg_text)
    cfg1 = load_config(path)
    cfg1.calendar.holidays_source = 'csv'
    cfg1.indicators.params['ema'].append(99)
    cfg2 = load_config(path)
    assert cfg2.calendar.holidays_source == 'none'
    assert 99 not in cfg2.indicators.params['ema']


def test_load_config_invalid_yaml():
    path = _write_cfg("- just\n- a\n- list\n")
    with pytest.raises(TypeError):
        load_config(path)
