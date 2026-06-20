# Project Brief — Book 2 Ch20 Vector Autoregression

## Student attribution

| Role | Name | Roll No | Project title |
|---|---|---|---|
| **Primary** | KASHIF AKRAM | `S22BINFT1M01203` | Visualization of Collaborative Learning Networks Using igraph (cross-fit) |
| Secondary | AHMAD SAJJAD | `F22BINFT1M01253` | Temporal Network Analysis for Understanding Student Collaboration Over Time (cross-listed) |

Section: Fall 2025 BSIT (7th semester) FYP cohort.


## Source
- *Advanced Learning Analytics Methods: AI, Precision and Complexity* (Saqr, López-Pernas et al., Springer 2025)
- Chapter `book2/ch20-var/` (CC BY-NC-SA 4.0)

## FYP framing
Translate the chapter's R/Quarto analysis into a Python pipeline + a FastAPI
live-prediction service. The student uses the dashboard's form to submit
inputs and receives the model's prediction via HTTP.

## Methodology
TODO: capture the chapter's modelling choices, data preparation, and outputs.

## Deliverables
- `backend/run_var_pipeline.py` — reproduces the chapter's analysis in Python.
- `backend/api.py` — FastAPI endpoint `/predict`.
- `frontend/` — manual-input dashboard that POSTs to the API.
- `outputs/backend/dashboard.json` — artifact consumed by the frontend.
