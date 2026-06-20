"""Offline pipeline for book-2 ch20 (Vector Autoregression).

Translates book2/ch20-var/ch20-var.qmd:
  - Load srl/srl.csv (longitudinal SRL self-reports, 36 learners x 156 days).
  - Filter to one focal learner ("Alice") and fit VAR(1) on a small set of
    SRL constructs (efficacy, value, planning, monitoring, effort).
  - Save fitted VAR model so api.py can produce one-step forecasts from a
    user-supplied recent observation.
"""
from __future__ import annotations
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR

SEED = 256
PERSON = "Alice"
SERIES_COLS = ["efficacy", "value", "planning", "monitoring", "effort"]


def project_paths():
    here = Path(__file__).resolve().parent
    project_root = here.parent
    return {
        "data_csv": project_root.parent / "book2-data" / "srl" / "srl.csv",
        "raw_local": project_root / "data" / "raw" / "srl.csv",
        "out": project_root / "outputs" / "backend",
        "models": project_root / "outputs" / "backend" / "models",
    }


def main():
    paths = project_paths()
    paths["out"].mkdir(parents=True, exist_ok=True)
    paths["models"].mkdir(parents=True, exist_ok=True)
    paths["raw_local"].parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(paths["data_csv"])
    df.to_csv(paths["raw_local"], index=False)
    person = df[df["name"] == PERSON][SERIES_COLS].dropna().reset_index(drop=True)
    if len(person) < 30:
        raise RuntimeError(f"Not enough rows for {PERSON} ({len(person)})")

    model = VAR(person.values)
    fitted = model.fit(1)
    coef = fitted.coefs[0]
    intercept = fitted.intercept

    in_sample = fitted.fittedvalues
    resid = person.values[1:] - in_sample
    rmse_per_var = np.sqrt(np.mean(resid ** 2, axis=0))

    last_row = person.iloc[-1].to_dict()

    joblib.dump({"coef": coef, "intercept": intercept,
                 "series_cols": SERIES_COLS, "last_row": last_row,
                 "rmse_per_var": rmse_per_var.tolist()},
                paths["models"] / "var.joblib")

    field_schema = []
    for col in SERIES_COLS:
        v = person[col]
        field_schema.append({
            "name": col, "label": col,
            "default": round(float(v.iloc[-1]), 3),
            "min": round(float(v.min()), 3), "max": round(float(v.max()), 3),
            "step": 0.01,
            "description": f"{PERSON}'s observed range: {v.min():.2f} to {v.max():.2f}",
        })

    payload = {
        "project": {
            "title": "Book-2 Ch20 Vector Autoregression",
            "source_chapter": "book2 ch20-var",
            "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "person": PERSON,
        },
        "overview": {
            "rows": int(len(person)),
            "lag": 1,
            "variables": SERIES_COLS,
            "rmse_per_var": dict(zip(SERIES_COLS, [round(float(r), 4) for r in rmse_per_var])),
        },
        "coefficients": coef.round(4).tolist(),
        "intercept": intercept.round(4).tolist(),
        "manual_demo": {
            "input_type": "tabular",
            "feature_order": SERIES_COLS,
            "field_schema": field_schema,
            "person": PERSON,
        },
    }
    (paths["out"] / "dashboard.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"VAR(1) fitted for {PERSON} on {len(person)} obs; RMSE_per_var={rmse_per_var.round(3).tolist()}")


if __name__ == "__main__":
    main()
