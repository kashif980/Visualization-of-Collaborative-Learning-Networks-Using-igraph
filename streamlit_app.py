"""Streamlit frontend for Book-2 Chapter 20 Vector Autoregression.

Run with:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


APP_TITLE = "Collaborative Learning VAR Studio"
PROJECT_TITLE = "Visualization of Collaborative Learning Networks Using igraph"
PROJECT_ROOT = Path(__file__).resolve().parent
DASHBOARD_PATH = PROJECT_ROOT / "outputs" / "backend" / "dashboard.json"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "srl.csv"
BACKEND_DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "backend_alice_var_dataset.csv"
DEFAULT_API_PORT = 9620

PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#e8edf5"},
    "xaxis": {"showgrid": False, "zeroline": False, "linecolor": "#293340"},
    "yaxis": {"gridcolor": "rgba(160, 174, 192, .16)", "zeroline": False},
}


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        --bg: #0b0f13;
        --panel: #141b22;
        --panel-soft: #19222c;
        --ink: #f4f7fb;
        --muted: #aab6c5;
        --line: #293340;
        --teal: #2dd4bf;
        --blue: #60a5fa;
        --amber: #f59e0b;
        --danger: #fb7185;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 10% 0%, rgba(45, 212, 191, .12), transparent 28rem),
            radial-gradient(circle at 86% 16%, rgba(96, 165, 250, .10), transparent 26rem),
            linear-gradient(180deg, #0b0f13 0%, #111821 54%, #0b0f13 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] {
        background: rgba(11, 15, 19, .86);
        border-bottom: 1px solid rgba(41, 51, 64, .7);
    }
    .main .block-container {
        max-width: 1220px;
        padding-top: 1.4rem;
        padding-bottom: 2.25rem;
    }
    [data-testid="stSidebar"] {
        background: #080c10;
        border-right: 1px solid var(--line);
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: var(--ink);
    }
    div[data-testid="stCaptionContainer"], small {
        color: var(--muted) !important;
    }
    hr {
        border-color: var(--line);
    }
    .hero {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 1.05rem;
        align-items: center;
        background: linear-gradient(135deg, rgba(25, 34, 44, .96), rgba(13, 18, 24, .96));
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 24px 70px rgba(0, 0, 0, .27);
    }
    .network-mark {
        width: 74px;
        height: 74px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        background: rgba(45, 212, 191, .12);
        border: 1px solid rgba(45, 212, 191, .36);
    }
    .network-mark svg {
        width: 50px;
        height: 50px;
    }
    .kicker {
        color: var(--teal);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .3rem;
    }
    .hero h1 {
        margin: 0;
        font-size: clamp(1.75rem, 3.2vw, 2.8rem);
        line-height: 1.08;
        font-weight: 820;
    }
    .hero p {
        margin: .6rem 0 0;
        max-width: 820px;
        color: var(--muted);
        line-height: 1.55;
        font-size: .98rem;
    }
    .metric-card {
        min-height: 104px;
        background: linear-gradient(180deg, rgba(25, 34, 44, .96), rgba(20, 27, 34, .96));
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 18px 46px rgba(0, 0, 0, .2);
    }
    .metric-label {
        color: var(--muted);
        font-size: .8rem;
        font-weight: 700;
        letter-spacing: .04em;
        text-transform: uppercase;
    }
    .metric-value {
        margin-top: .34rem;
        color: var(--ink);
        font-size: 1.42rem;
        font-weight: 780;
        word-break: break-word;
    }
    .metric-subtle {
        margin-top: .28rem;
        color: var(--muted);
        font-size: .86rem;
    }
    .section-note {
        color: var(--muted);
        font-size: .95rem;
        line-height: 1.5;
        max-width: 850px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        border: 1px solid rgba(45, 212, 191, .32);
        border-radius: 999px;
        background: rgba(45, 212, 191, .09);
        color: #d7fffa;
        font-size: .86rem;
        font-weight: 720;
        padding: .35rem .62rem;
    }
    div[data-testid="stForm"],
    [data-testid="stExpander"] {
        background: rgba(20, 27, 34, .94);
        border: 1px solid var(--line);
        border-radius: 8px;
    }
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 8px;
        min-height: 2.75rem;
        font-weight: 760;
    }
    .app-footer {
        color: var(--muted);
        border-top: 1px solid var(--line);
        margin-top: 2rem;
        padding-top: .85rem;
        font-size: .88rem;
        text-align: center;
    }
    @media (max-width: 760px) {
        .hero {
            grid-template-columns: 1fr;
        }
        .network-mark {
            width: 58px;
            height: 58px;
        }
        .network-mark svg {
            width: 40px;
            height: 40px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_dashboard() -> Optional[Dict[str, Any]]:
    if not DASHBOARD_PATH.exists():
        return None
    return json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_raw_data() -> Optional[pd.DataFrame]:
    if not RAW_DATA_PATH.exists():
        return None
    return pd.read_csv(RAW_DATA_PATH)


def get_api_port() -> int:
    try:
        return int(st.secrets.get("api_port", DEFAULT_API_PORT))
    except Exception:
        return DEFAULT_API_PORT


def api_health(api_port: int) -> Tuple[bool, str]:
    for endpoint in ("health", ""):
        try:
            response = requests.get(f"http://127.0.0.1:{api_port}/{endpoint}", timeout=3)
            if response.status_code < 500:
                return True, f"FastAPI reachable on port {api_port}"
        except requests.RequestException:
            pass
    return False, f"FastAPI not reachable on port {api_port}"


def start_fastapi_server(api_port: int) -> Tuple[bool, str]:
    out_log = PROJECT_ROOT / "fastapi_backend.out.log"
    err_log = PROJECT_ROOT / "fastapi_backend.err.log"

    startupinfo = None
    if sys.platform.startswith("win"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    with out_log.open("a", encoding="utf-8") as stdout, err_log.open("a", encoding="utf-8") as stderr:
        subprocess.Popen(
            [
                sys.executable,
                "backend_runner.py",
            ],
            cwd=PROJECT_ROOT,
            stdout=stdout,
            stderr=stderr,
            startupinfo=startupinfo,
        )

    for _ in range(12):
        time.sleep(0.5)
        ok, message = api_health(api_port)
        if ok:
            return True, message
    return False, "Direct backend fallback ready"


def ensure_fastapi_connected(api_port: int) -> Tuple[bool, str]:
    ok, message = api_health(api_port)
    if ok:
        return ok, message
    return start_fastapi_server(api_port)


def call_backend(values: Dict[str, float], api_port: int) -> Dict[str, Any]:
    ok, _ = ensure_fastapi_connected(api_port)
    if not ok:
        from backend.api import predict

        return predict({"values": values})

    response = requests.post(
        f"http://127.0.0.1:{api_port}/predict",
        json={"values": values},
        timeout=12,
    )
    response.raise_for_status()
    return response.json()


def prediction_tables(payload: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    prediction = payload.get("prediction", {})
    forecast = prediction.get("one_step_forecast", {})
    rmse = prediction.get("rmse_per_variable", {})
    echo = payload.get("echo", {}).get("current_state", {})

    forecast_df = pd.DataFrame(
        [{"variable": key, "current": echo.get(key), "forecast": value} for key, value in forecast.items()]
    )
    if not forecast_df.empty:
        forecast_df["change"] = forecast_df["forecast"] - forecast_df["current"]

    rmse_df = pd.DataFrame([{"variable": key, "rmse": value} for key, value in rmse.items()])
    echo_df = pd.DataFrame([{"variable": key, "value": value} for key, value in echo.items()])
    return forecast_df, rmse_df, echo_df


def forecast_chart(forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=forecast_df["variable"],
            y=forecast_df["current"],
            name="Current",
            marker_color="#7c8da3",
        )
    )
    fig.add_trace(
        go.Bar(
            x=forecast_df["variable"],
            y=forecast_df["forecast"],
            name="Forecast",
            marker_color="#2dd4bf",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="group",
        height=385,
        margin=dict(l=20, r=20, t=38, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Score",
        xaxis_title="",
    )
    return fig


def rmse_chart(rmse_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=rmse_df["rmse"],
            y=rmse_df["variable"],
            orientation="h",
            marker_color="#f59e0b",
            text=rmse_df["rmse"].round(3),
            textposition="auto",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=300,
        margin=dict(l=20, r=20, t=18, b=20),
        xaxis_title="RMSE",
        yaxis_title="",
    )
    return fig


def history_chart(raw_df: pd.DataFrame, person: str, variables: list[str]) -> go.Figure:
    view = raw_df.copy()
    if "name" in view.columns:
        view = view[view["name"] == person]

    x_values = view["day"] if "day" in view.columns else list(range(1, len(view) + 1))
    fig = go.Figure()
    colors = ["#2dd4bf", "#60a5fa", "#f59e0b", "#c084fc", "#94a3b8"]
    for variable in variables:
        if variable not in view.columns:
            continue
        color = colors[len(fig.data) % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=view[variable],
                mode="lines+markers",
                name=variable.title(),
                line=dict(color=color, width=2.3),
                marker=dict(size=6, color=color, line=dict(color="#0b0f13", width=1)),
            )
        )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=360,
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title="Observation",
        yaxis_title="Score",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render_header(dashboard: Optional[Dict[str, Any]], backend_ok: bool, backend_message: str) -> None:
    person = (dashboard or {}).get("project", {}).get("person", "learner")
    status_color = "#2dd4bf" if backend_ok else "#f59e0b"
    st.markdown(
        f"""
        <div class="hero">
            <div class="network-mark" aria-hidden="true">
                <svg viewBox="0 0 64 64" role="img">
                    <line x1="15" y1="18" x2="34" y2="12" stroke="#2dd4bf" stroke-width="3" />
                    <line x1="34" y1="12" x2="50" y2="25" stroke="#60a5fa" stroke-width="3" />
                    <line x1="15" y1="18" x2="24" y2="44" stroke="#f59e0b" stroke-width="3" />
                    <line x1="24" y1="44" x2="48" y2="47" stroke="#2dd4bf" stroke-width="3" />
                    <line x1="50" y1="25" x2="48" y2="47" stroke="#7c8da3" stroke-width="3" />
                    <line x1="34" y1="12" x2="24" y2="44" stroke="#2dd4bf" stroke-width="3" opacity=".72" />
                    <circle cx="15" cy="18" r="6" fill="#2dd4bf" />
                    <circle cx="34" cy="12" r="6" fill="#f8fafc" />
                    <circle cx="50" cy="25" r="6" fill="#60a5fa" />
                    <circle cx="24" cy="44" r="6" fill="#f59e0b" />
                    <circle cx="48" cy="47" r="6" fill="#2dd4bf" />
                </svg>
            </div>
            <div>
                <div class="kicker">Book 2 / Chapter 20 - VAR(1) Forecasting</div>
                <h1>{PROJECT_TITLE}</h1>
                <p>
                    A presentation-ready dashboard for {person}'s self-regulated
                    learning measures, combining manual forecasting, backend health,
                    model error summaries, and trend exploration in one place.
                </p>
                <div style="margin-top:.75rem;">
                    <span class="status-pill">
                        <span style="width:.55rem;height:.55rem;border-radius:999px;background:{status_color};display:inline-block;"></span>
                        {backend_message}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(dashboard: Dict[str, Any], backend_ok: bool) -> None:
    overview = dashboard.get("overview", {})
    project = dashboard.get("project", {})
    variables = overview.get("variables", [])
    generated_at = project.get("generated_at", "Not available")
    metrics = [
        ("Learner", project.get("person", dashboard.get("manual_demo", {}).get("person", "N/A")), "Focused analysis"),
        ("Observations", overview.get("rows", "N/A"), "Rows used by model"),
        ("Lag", f"VAR({overview.get('lag', 1)})", "One-step forecast"),
        ("Backend", "Online" if backend_ok else "Offline", generated_at),
        ("Variables", len(variables), ", ".join(variables[:3]) + ("..." if len(variables) > 3 else "")),
    ]
    cols = st.columns(len(metrics))
    for col, (label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-subtle">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_prediction_panel(dashboard: Dict[str, Any], api_port: int) -> None:
    field_schema = dashboard.get("manual_demo", {}).get("field_schema", [])
    variables = dashboard.get("manual_demo", {}).get("feature_order") or dashboard.get("overview", {}).get("variables", [])

    st.subheader("Manual Prediction")
    st.markdown(
        '<div class="section-note">Enter the current learner state, call the FastAPI prediction endpoint, and compare the current values against the one-step VAR forecast.</div>',
        unsafe_allow_html=True,
    )

    if not field_schema:
        st.warning("No input schema found. Run `python backend/run_var_pipeline.py` first.")
        return

    left, right = st.columns([0.9, 1.35], gap="large")
    with left:
        with st.form("prediction_form"):
            st.markdown("#### Input Variables")
            input_values: Dict[str, float] = {}
            for field in field_schema:
                name = field["name"]
                input_values[name] = st.number_input(
                    label=field.get("label", name).title(),
                    value=float(field.get("default", 0)),
                    step=float(field.get("step", 0.01)),
                    min_value=float(field["min"]) if field.get("min") is not None else None,
                    max_value=float(field["max"]) if field.get("max") is not None else None,
                    help=field.get("description", ""),
                )
            submitted = st.form_submit_button("Run Prediction", use_container_width=True, type="primary")

        with st.expander("API request preview"):
            st.json({"values": input_values})

    with right:
        st.markdown("#### Results")
        if submitted:
            try:
                with st.spinner("Calling FastAPI and generating forecast..."):
                    st.session_state["latest_prediction"] = call_backend(input_values, api_port)
                st.success("Prediction completed.")
            except requests.ConnectionError:
                st.error(f"Backend unreachable on port {api_port}. Start FastAPI and try again.")
                st.code(f"python -m uvicorn backend.api:app --host 127.0.0.1 --port {api_port}", language="powershell")
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Backend error: {detail}")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

        payload = st.session_state.get("latest_prediction")
        if not payload:
            st.info("Run a prediction to see the forecast chart and model error summary.")
            return

        forecast_df, rmse_df, echo_df = prediction_tables(payload)
        if forecast_df.empty:
            st.warning("The backend response did not include forecast values.")
            st.json(payload)
            return

        st.plotly_chart(forecast_chart(forecast_df), use_container_width=True)
        st.dataframe(forecast_df.round(4), use_container_width=True, hide_index=True)

        tabs = st.tabs(["RMSE", "Current State", "Raw API"])
        with tabs[0]:
            if rmse_df.empty:
                st.info("No RMSE values returned by backend.")
            else:
                st.plotly_chart(rmse_chart(rmse_df), use_container_width=True)
                st.dataframe(rmse_df.round(4), use_container_width=True, hide_index=True)
        with tabs[1]:
            st.dataframe(echo_df.round(4), use_container_width=True, hide_index=True)
        with tabs[2]:
            st.json(payload)

    raw_df = load_raw_data()
    if raw_df is not None and variables:
        person = dashboard.get("project", {}).get("person", dashboard.get("manual_demo", {}).get("person", "Alice"))
        st.divider()
        st.subheader("Recent Learning Trend")
        st.plotly_chart(history_chart(raw_df, person, variables), use_container_width=True)


def render_model_summary(dashboard: Dict[str, Any]) -> None:
    variables = dashboard.get("overview", {}).get("variables", [])
    coefficients = dashboard.get("coefficients", [])
    intercept = dashboard.get("intercept", [])

    st.subheader("Model Summary")
    st.markdown(
        '<div class="section-note">Use these backend artifacts during presentation to explain model structure, relationships, and prediction uncertainty.</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1.15, 0.85], gap="large")
    with col_a:
        if coefficients and variables:
            coef_df = pd.DataFrame(coefficients, index=variables, columns=variables)
            coef_df.index.name = "forecast_variable"
            st.caption("Coefficient matrix")
            st.dataframe(coef_df.round(4), use_container_width=True)
        else:
            st.info("Coefficient matrix is not available.")

    with col_b:
        rmse = dashboard.get("overview", {}).get("rmse_per_var", {})
        if rmse:
            rmse_df = pd.DataFrame([{"variable": key, "rmse": value} for key, value in rmse.items()])
            st.caption("Error by variable")
            st.plotly_chart(rmse_chart(rmse_df), use_container_width=True)
        if intercept and variables:
            st.caption("Intercept terms")
            st.dataframe(
                pd.DataFrame({"variable": variables, "intercept": intercept}).round(4),
                use_container_width=True,
                hide_index=True,
            )


def render_dataset_download() -> None:
    st.subheader("Dataset Download")
    st.markdown(
        '<div class="section-note">Download the exact CSV used by the backend VAR model for Alice.</div>',
        unsafe_allow_html=True,
    )

    if not BACKEND_DATASET_PATH.exists():
        st.warning("Backend dataset CSV was not found at `data/raw/backend_alice_var_dataset.csv`.")
        return

    st.download_button(
        label="Download backend_alice_var_dataset.csv",
        data=BACKEND_DATASET_PATH.read_bytes(),
        file_name="backend_alice_var_dataset.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )


def main() -> None:
    dashboard = load_dashboard()
    api_port = get_api_port()
    backend_ok, backend_message = ensure_fastapi_connected(api_port)

    with st.sidebar:
        st.header("Controls")
        page = st.radio("View", ["Prediction Studio", "Model Summary"], label_visibility="collapsed")
        st.divider()
        st.caption("Runtime")
        st.write(f"FastAPI port: `{api_port}`")
        if backend_ok:
            st.success(backend_message)
        else:
            st.warning(backend_message)
            st.code(f"python -m uvicorn backend.api:app --host 127.0.0.1 --port {api_port}", language="powershell")

    render_header(dashboard, backend_ok, backend_message)
    st.divider()

    if dashboard is None:
        st.error(f"Dashboard data not found at `{DASHBOARD_PATH}`")
        st.info("Run `python backend/run_var_pipeline.py`, then refresh this app.")
        return

    render_metric_cards(dashboard, backend_ok)
    st.divider()

    if page == "Prediction Studio":
        render_prediction_panel(dashboard, api_port)
    else:
        render_model_summary(dashboard)

    st.markdown(
        """
        <div class="app-footer">
            Advanced LA Methods FYP - Book 2 / Chapter 20
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
