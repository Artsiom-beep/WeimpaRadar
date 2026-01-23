from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from radar_py.export.csv_v0_1 import write_data_csv_v0_1
from radar_py.llm.generate import generate_sales_and_report
from radar_py.utils.fs import write_json


def write_outputs(
    data: Dict[str, Any],
    run_dir: Path,
) -> None:
    """
    Записывает все финальные артефакты run:
    - sales_note.txt
    - report.md
    - data.json
    - data.csv
    """
    sales_path, report_path = generate_sales_and_report(data, run_dir)
    data["outputs"]["sales_note_txt"] = sales_path
    data["outputs"]["report_md"] = report_path

    data_path = run_dir / "data.json"
    data["outputs"]["data_json"] = str(data_path.as_posix())
    write_json(data_path, data)

    csv_path = run_dir / "data.csv"
    data["outputs"]["data_csv"] = write_data_csv_v0_1(data, csv_path)

    # финальная фиксация data.json (как и в текущем коде)
    write_json(data_path, data)
