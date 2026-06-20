"""FastAPI server for book-2 ch20 (Vector Autoregression).

POST /predict with the most recent observation -> one-step VAR(1) forecast.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SHARED = _PROJECT_ROOT.parent / "fyp-shared" / "python"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from fyp_shared.api import create_app  # noqa: E402

_DASHBOARD_PATH = _PROJECT_ROOT / "outputs" / "backend" / "dashboard.json"
_MODEL_PATH = _PROJECT_ROOT / "outputs" / "backend" / "models" / "var.joblib"


def _load():
    data = json.loads(_DASHBOARD_PATH.read_text(encoding="utf-8"))
    return data, joblib.load(_MODEL_PATH)


_DATA, _M = _load()
_SERIES_COLS: List[str] = list(_M["series_cols"])
_COEF = np.asarray(_M["coef"])
_INTERCEPT = np.asarray(_M["intercept"])
_RMSE = list(_M["rmse_per_var"])

_SCHEMA = {
    "input_type": "tabular",
    "feature_order": _SERIES_COLS,
    "field_schema": _DATA["manual_demo"]["field_schema"],
    "person": _M.get("series_cols") and _DATA["manual_demo"]["person"],
}


def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    values = payload.get("values", payload)
    if not isinstance(values, dict):
        raise ValueError("payload.values must be an object")
    row: List[float] = []
    for col in _SERIES_COLS:
        if col not in values:
            raise ValueError(f"missing variable: {col}")
        try:
            row.append(float(values[col]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"variable {col!r} is not numeric") from exc
    arr = np.asarray(row, dtype=float)
    forecast = _INTERCEPT + _COEF @ arr
    return {
        "prediction": {
            "one_step_forecast": {col: round(float(forecast[i]), 4) for i, col in enumerate(_SERIES_COLS)},
            "rmse_per_variable": dict(zip(_SERIES_COLS, [round(float(r), 4) for r in _RMSE])),
        },
        "echo": {"current_state": dict(zip(_SERIES_COLS, row))},
    }


app = create_app(
    title="Book-2 Ch20 VAR",
    predict_fn=predict,
    schema_dict=_SCHEMA,
)
