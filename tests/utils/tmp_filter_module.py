import sys
import uuid
from pathlib import Path


def write_tmp_filters_module(tmpdir, items):
    """Write a temporary filters module.

    Parameters
    ----------
    tmpdir : path-like
        Directory where module file will be created.
    items : list[dict]
        List of filter definitions (FilterCode/PythonQuery).

    Returns
    -------
    str
        Importable module name.
    """
    mod_name = f"tmp_filters_{uuid.uuid4().hex[:8]}"
    mod_path = Path(tmpdir) / f"{mod_name}.py"
    body = (
        "FILTERS = " + repr([{k: v for k, v in i.items()} for i in items]) + "\n"
        + "def get_filters():\n    return FILTERS\n"
    )
    mod_path.write_text(body, encoding="utf-8")
    if str(tmpdir) not in sys.path:
        sys.path.insert(0, str(tmpdir))
    return mod_name
