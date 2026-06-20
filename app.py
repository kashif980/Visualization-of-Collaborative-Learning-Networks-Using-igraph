"""Streamlit frontend for Book-2 Chapter 20 Vector Autoregression.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


APP_TITLE = "Visualization of Collaborative Learning Networks Using igraph"
NAV_OVERVIEW = "🏠 Overview"
NAV_NETWORK = "🌐 Network Visualization"
NAV_ANALYTICS = "📊 Graph Analytics"
NAV_DATA = "📁 Data Explorer"
NAV_RESULTS = "📈 Insights & Findings"
NAV_ABOUT = "ℹ️ About Project"
PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#edf2f7"},
    "xaxis": {"showgrid": False, "zeroline": False, "linecolor": "#2a3442"},
    "yaxis": {"gridcolor": "rgba(174, 184, 198, .12)", "zeroline": False},
}


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="expanded",
)


PROJECT_ROOT = Path(__file__).resolve().parent
DASHBOARD_PATH = PROJECT_ROOT / "outputs" / "backend" / "dashboard.json"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "srl.csv"
BACKEND_DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "backend_alice_var_dataset.csv"
DEFAULT_API_PORT = 9620


st.markdown(
    """
    <style>
    :root {
        --bg: #0c0f14;
        --bg-soft: #11161d;
        --panel: #151b23;
        --panel-soft: #1b2430;
        --ink: #f4f7fb;
        --muted: #aeb8c6;
        --line: #2a3442;
        --teal: #2dd4bf;
        --teal-soft: rgba(45, 212, 191, .14);
        --amber: #f59e0b;
        --steel: #7c8da3;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(45, 212, 191, .10), transparent 34rem),
            linear-gradient(180deg, #0c0f14 0%, #10141b 48%, #0c0f14 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] {
        background: rgba(12, 15, 20, 0.88);
        border-bottom: 1px solid rgba(42, 52, 66, 0.72);
    }
    .main .block-container {
        padding-top: 1.35rem;
        padding-bottom: 2.2rem;
        max-width: 1220px;
    }
    [data-testid="stSidebar"] {
        background: #090c11;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * {
        color: var(--ink);
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: var(--ink);
    }
    div[data-testid="stCaptionContainer"], .stCaptionContainer, small {
        color: var(--muted) !important;
    }
    hr {
        border-color: var(--line);
    }
    .hero-shell {
        display: flex;
        align-items: center;
        gap: 1.15rem;
        background: linear-gradient(135deg, rgba(27, 36, 48, .96), rgba(16, 21, 28, .96));
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 22px 70px rgba(0, 0, 0, .28);
    }
    .network-mark {
        width: 72px;
        height: 72px;
        flex: 0 0 72px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        background: var(--teal-soft);
        border: 1px solid rgba(45, 212, 191, .35);
    }
    .network-mark svg {
        width: 48px;
        height: 48px;
    }
    .hero-kicker {
        color: var(--teal);
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .25rem;
    }
    .hero-title {
        color: var(--ink);
        font-size: clamp(1.7rem, 3.2vw, 2.8rem);
        line-height: 1.06;
        font-weight: 820;
        margin: 0;
    }
    .hero-copy {
        color: var(--muted);
        max-width: 780px;
        font-size: .98rem;
        line-height: 1.55;
        margin-top: .6rem;
    }
    .metric-card {
        background: linear-gradient(180deg, rgba(27, 36, 48, .96), rgba(21, 27, 35, .96));
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 104px;
        box-shadow: 0 18px 48px rgba(0, 0, 0, .22);
    }
    .metric-label {
        color: var(--muted);
        font-size: .82rem;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: .04em;
    }
    .metric-value {
        color: var(--ink);
        font-size: 1.45rem;
        font-weight: 760;
        margin-top: .35rem;
    }
    .section-note {
        color: var(--muted);
        font-size: .95rem;
        line-height: 1.5;
        max-width: 860px;
    }
    .about-panel {
        background: linear-gradient(180deg, rgba(27, 36, 48, .96), rgba(21, 27, 35, .96));
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem 1.05rem;
        min-height: 148px;
        box-shadow: 0 18px 48px rgba(0, 0, 0, .18);
    }
    .about-panel h3 {
        font-size: 1rem;
        margin: 0 0 .55rem;
        color: var(--ink);
    }
    .about-panel p,
    .about-panel li {
        color: var(--muted);
        font-size: .93rem;
        line-height: 1.55;
    }
    .about-panel ul {
        margin: 0;
        padding-left: 1.05rem;
    }
    .about-badge {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        margin: .18rem .32rem .18rem 0;
        padding: .32rem .55rem;
        border: 1px solid rgba(45, 212, 191, .28);
        border-radius: 999px;
        background: rgba(45, 212, 191, .08);
        color: #d8fffa;
        font-size: .84rem;
        font-weight: 680;
    }
    .command-box {
        margin-top: .55rem;
        padding: .85rem 1rem;
        border: 1px solid rgba(45, 212, 191, .36);
        border-radius: 8px;
        background: #071114;
        color: #7fffe9;
        font-family: Consolas, "Courier New", monospace;
        font-size: .95rem;
        font-weight: 700;
        letter-spacing: .01em;
    }
    [data-testid="stExpander"],
    div[data-testid="stForm"] {
        background: rgba(21, 27, 35, .94);
        border: 1px solid var(--line);
        border-radius: 8px;
    }
    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: .85rem .95rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
    }
    .stButton > button {
        border-radius: 7px;
        font-weight: 700;
        border: 1px solid rgba(45, 212, 191, .72);
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        color: #f8fafc;
    }
    .stButton > button:hover {
        border-color: #99f6e4;
        background: linear-gradient(135deg, #0d9488, #2dd4bf);
        color: #071014;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] > div,
    textarea {
        background: #0f172a !important;
        border-color: var(--line) !important;
        color: var(--ink) !important;
    }
    [data-testid="stAlert"] {
        border-radius: 8px;
    }
    [data-testid="stAlert"] * {
        color: #f4f7fb !important;
    }
    [data-testid="stCodeBlock"],
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] code {
        background: #0a0f16 !important;
        color: #e6fffb !important;
        border-color: var(--line) !important;
    }
    code {
        color: #e6fffb !important;
        background: rgba(45, 212, 191, .10) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: #111820;
        border: 1px solid var(--line);
        border-radius: 7px;
        padding: .45rem .8rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(45, 212, 191, .16);
        border-color: var(--teal);
        color: var(--teal);
    }
    .app-footer {
        margin-top: 2.4rem;
        padding: 1.05rem 0 .35rem;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: .92rem;
        text-align: center;
    }
    .app-footer strong {
        color: var(--teal);
        font-size: 1.08rem;
        font-weight: 800;
        letter-spacing: .01em;
    }
    @media (max-width: 700px) {
        .hero-shell {
            align-items: flex-start;
            gap: .85rem;
            padding: 1rem;
        }
        .network-mark {
            width: 56px;
            height: 56px;
            flex-basis: 56px;
        }
        .network-mark svg {
            width: 38px;
            height: 38px;
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


def get_field_schema(dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
    return dashboard.get("manual_demo", {}).get("field_schema", [])


def get_feature_order(dashboard: Dict[str, Any]) -> List[str]:
    manual_order = dashboard.get("manual_demo", {}).get("feature_order", [])
    overview_order = dashboard.get("overview", {}).get("variables", [])
    return list(manual_order or overview_order)


def call_direct_backend(values: Dict[str, float]) -> Dict[str, Any]:
    from backend.api import predict

    return predict({"values": values})


def call_api_backend(values: Dict[str, float], api_port: int) -> Dict[str, Any]:
    ok, _ = ensure_api_health(api_port)
    if not ok:
        return call_direct_backend(values)

    response = requests.post(
        f"http://127.0.0.1:{api_port}/predict",
        json={"values": values},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def api_health(api_port: int) -> Tuple[bool, str]:
    try:
        response = requests.get(f"http://127.0.0.1:{api_port}/health", timeout=3)
        if response.ok:
            return True, "Connected"
        return False, f"HTTP {response.status_code}"
    except requests.RequestException:
        return False, "Starting backend..."


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


def ensure_api_health(api_port: int) -> Tuple[bool, str]:
    ok, message = api_health(api_port)
    if ok:
        return ok, message
    return start_fastapi_server(api_port)


def prediction_tables(payload: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    prediction = payload.get("prediction", {})
    forecast = prediction.get("one_step_forecast", {})
    rmse = prediction.get("rmse_per_variable", {})
    echo = payload.get("echo", {}).get("current_state", {})

    forecast_df = pd.DataFrame(
        [{"variable": key, "forecast": value, "current": echo.get(key)} for key, value in forecast.items()]
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
        height=380,
        margin=dict(l=20, r=20, t=35, b=20),
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
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="RMSE",
        yaxis_title="",
    )
    return fig


def history_chart(raw_df: pd.DataFrame, person: str, variables: List[str]) -> go.Figure:
    view = raw_df.copy()
    if "name" in view.columns:
        view = view[view["name"] == person]

    x_values = view["day"] if "day" in view.columns else list(range(1, len(view) + 1))
    fig = go.Figure()
    colors = ["#2dd4bf", "#f59e0b", "#60a5fa", "#c084fc", "#94a3b8"]
    for variable in variables:
        if variable in view.columns:
            color = colors[len(fig.data) % len(colors)]
            series = view[variable]
            fig.add_trace(
                go.Scatter(
                    x=x_values,
                    y=series,
                    mode="lines+markers",
                    name=variable,
                    line=dict(color=color, width=2.4),
                    marker=dict(
                        color=color,
                        size=6,
                        line=dict(color="#0c0f14", width=1),
                        opacity=.9,
                    ),
                )
            )
            if len(series) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=[x_values.iloc[-1] if hasattr(x_values, "iloc") else x_values[-1]],
                        y=[series.iloc[-1]],
                        mode="markers",
                        name=f"{variable} latest",
                        showlegend=False,
                        marker=dict(
                            color=color,
                            size=13,
                            symbol="circle",
                            line=dict(color="#f8fafc", width=2),
                        ),
                        hovertemplate=f"{variable} latest<br>Observation=%{{x}}<br>Score=%{{y:.2f}}<extra></extra>",
                    )
                )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=430,
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title="Observation",
        yaxis_title="Score",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render_header(dashboard: Optional[Dict[str, Any]]) -> None:
    project = (dashboard or {}).get("project", {})
    person = project.get("person", "focal learner")

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="network-mark" aria-hidden="true">
                <svg viewBox="0 0 64 64" role="img">
                    <line x1="16" y1="18" x2="34" y2="12" stroke="#2dd4bf" stroke-width="3" />
                    <line x1="34" y1="12" x2="50" y2="25" stroke="#f59e0b" stroke-width="3" />
                    <line x1="16" y1="18" x2="24" y2="44" stroke="#7c8da3" stroke-width="3" />
                    <line x1="24" y1="44" x2="48" y2="47" stroke="#2dd4bf" stroke-width="3" />
                    <line x1="50" y1="25" x2="48" y2="47" stroke="#7c8da3" stroke-width="3" />
                    <line x1="34" y1="12" x2="24" y2="44" stroke="#2dd4bf" stroke-width="3" opacity=".75" />
                    <circle cx="16" cy="18" r="6" fill="#2dd4bf" />
                    <circle cx="34" cy="12" r="6" fill="#f8fafc" />
                    <circle cx="50" cy="25" r="6" fill="#f59e0b" />
                    <circle cx="24" cy="44" r="6" fill="#7c8da3" />
                    <circle cx="48" cy="47" r="6" fill="#2dd4bf" />
                </svg>
            </div>
            <div>
                <h1 class="hero-title">{APP_TITLE}</h1>
                <div class="hero-copy">
                    A graph-based analytical dashboard for exploring collaborative
                    learning networks. It enables structured analysis of learner
                    interactions, visualization of network relationships, and
                    presentation of graph-based insights through interactive views,
                    tables, and summary statistics.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(dashboard: Dict[str, Any]) -> None:
    overview = dashboard.get("overview", {})
    project = dashboard.get("project", {})
    variables = overview.get("variables", [])
    metrics = [
        ("Selected Entity", project.get("person", "Learning data")),
        ("Total Observations", overview.get("rows", "N/A")),
        ("Analysis Status", "Backend Computed"),
        ("Analytical Measures", len(variables)),
    ]
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_prediction_form(
    dashboard: Dict[str, Any],
    backend_mode: str,
    api_port: int,
) -> None:
    schema = get_field_schema(dashboard)
    variables = get_feature_order(dashboard)

    if not schema:
        st.error("Input schema is missing. Run `python backend/run_var_pipeline.py` to regenerate backend outputs.")
        return

    left, right = st.columns([0.95, 1.35], gap="large")
    uploaded_values: Dict[str, float] = {}

    st.subheader("Insights & Findings")
    st.markdown(
        '<div class="section-note">Submit learner measures and review the generated analytical output in a structured format.</div>',
        unsafe_allow_html=True,
    )

    with left:
        st.markdown("#### Analysis Input")
        st.markdown('<div class="section-note">Enter values manually or upload a CSV to use the latest complete record.</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Optional CSV upload", type=["csv"])
        if uploaded_file is not None:
            try:
                upload_df = pd.read_csv(uploaded_file)
                missing = [name for name in variables if name not in upload_df.columns]
                if missing:
                    st.warning(f"Uploaded CSV is missing: {', '.join(missing)}")
                elif upload_df.empty:
                    st.warning("Uploaded CSV has no rows.")
                else:
                    latest = upload_df[variables].dropna().tail(1)
                    if latest.empty:
                        st.warning("No complete row found for the required variables.")
                    else:
                        uploaded_values = latest.iloc[0].astype(float).to_dict()
                        st.success("Loaded the last complete uploaded row.")
                        st.dataframe(latest, use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(f"Could not read the uploaded CSV: {exc}")

        with st.form("prediction_form"):
            values: Dict[str, float] = {}
            for field in schema:
                name = field["name"]
                default_value = uploaded_values.get(name, field.get("default", 0.0))
                values[name] = st.number_input(
                    label=field.get("label", name).title(),
                    min_value=float(field.get("min", 0.0)),
                    max_value=float(field.get("max", 100.0)),
                    value=float(default_value),
                    step=float(field.get("step", 0.01)),
                    help=field.get("description", ""),
                )

            submitted = st.form_submit_button("Run forecast", use_container_width=True, type="primary")

    with right:
        st.markdown("#### Analytical Results")
        result_box = st.container()

        if submitted:
            try:
                with st.spinner("Processing forecast with the existing backend..."):
                    if backend_mode == "FastAPI server":
                        payload = call_api_backend(values, api_port)
                    else:
                        payload = call_direct_backend(values)
                st.session_state["latest_prediction"] = payload
                st.success("Forecast generated successfully.")
            except requests.ConnectionError:
                st.error(f"FastAPI backend is not reachable on port {api_port}. Start it or switch to direct Python mode.")
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"The backend returned an error: {detail}")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

        payload = st.session_state.get("latest_prediction")
        with result_box:
            if not payload:
                st.info("Run a forecast to view model output here.")
                return

            forecast_df, rmse_df, echo_df = prediction_tables(payload)
            if forecast_df.empty:
                st.warning("The backend response did not include forecast values.")
                st.json(payload)
                return

            st.plotly_chart(forecast_chart(forecast_df), use_container_width=True)
            st.dataframe(
                forecast_df.round(4),
                use_container_width=True,
                hide_index=True,
            )

            tabs = st.tabs(["RMSE", "Input Echo", "Raw Output"])
            with tabs[0]:
                st.plotly_chart(rmse_chart(rmse_df), use_container_width=True)
                st.dataframe(rmse_df.round(4), use_container_width=True, hide_index=True)
            with tabs[1]:
                st.dataframe(echo_df.round(4), use_container_width=True, hide_index=True)
            with tabs[2]:
                st.json(payload)


def render_model_insights(dashboard: Dict[str, Any]) -> None:
    variables = get_feature_order(dashboard)
    coefficients = dashboard.get("coefficients", [])
    intercept = dashboard.get("intercept", [])
    rmse = dashboard.get("overview", {}).get("rmse_per_var", {})

    st.subheader("Graph Analytics")
    st.markdown(
        '<div class="section-note">Review backend-generated relationships, error measures, and supporting analytical values.</div>',
        unsafe_allow_html=True,
    )
    col_a, col_b = st.columns([1.15, 0.85], gap="large")

    with col_a:
        if coefficients and variables:
            coef_df = pd.DataFrame(coefficients, index=variables, columns=variables)
            coef_df.index.name = "forecast_variable"
            st.caption("Relationship matrix")
            st.dataframe(coef_df.round(4), use_container_width=True)
        else:
            st.warning("Coefficient matrix is not available in dashboard.json.")

    with col_b:
        if rmse:
            rmse_df = pd.DataFrame([{"variable": key, "rmse": value} for key, value in rmse.items()])
            st.caption("Error by measure")
            st.plotly_chart(rmse_chart(rmse_df), use_container_width=True)
        if intercept and variables:
            intercept_df = pd.DataFrame({"variable": variables, "intercept": intercept})
            st.caption("Baseline terms")
            st.dataframe(intercept_df.round(4), use_container_width=True, hide_index=True)


def render_data_preview(dashboard: Dict[str, Any], title: str = "Data Explorer") -> None:
    raw_df = load_raw_data()
    variables = get_feature_order(dashboard)
    person = dashboard.get("project", {}).get("person", dashboard.get("manual_demo", {}).get("person", "Alice"))

    st.subheader(title)
    st.markdown(
        f'<div class="section-note">Explore recent learner records and highlighted trends for {person}.</div>',
        unsafe_allow_html=True,
    )
    if raw_df is None:
        st.warning("Raw data was not found at `data/raw/srl.csv`. Run the backend pipeline to create it.")
        return

    st.plotly_chart(history_chart(raw_df, person, variables), use_container_width=True)

    preview = raw_df.copy()
    if "name" in preview.columns:
        preview = preview[preview["name"] == person]

    st.caption(f"Recent records: {person}")
    visible_columns = [column for column in ["day", "name", *variables] if column in preview.columns]
    st.dataframe(preview[visible_columns].tail(20), use_container_width=True, hide_index=True)


def render_about(dashboard: Dict[str, Any], backend_mode: str, api_port: int) -> None:
    project = dashboard.get("project", {})
    overview = dashboard.get("overview", {})
    person = project.get("person", "Alice")
    variables = overview.get("variables", [])

    st.subheader("About Project")
    st.markdown(
        """
        <div class="section-note">
        This Final Year Project presents collaborative learning analytics through a
        focused Streamlit interface. The dashboard is designed for clear exploration,
        readable visual summaries, and professional presentation of analytical results.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown(
            """
            <div class="about-panel">
                <h3>Project Purpose</h3>
                <p>
                    The application helps organize and present learning data in a way
                    that is easy to inspect during an FYP demonstration. It keeps the
                    backend intact while improving the user-facing dashboard.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            """
            <div class="about-panel">
                <h3>Key Objectives</h3>
                <ul>
                    <li>Explore learner records through clean visual summaries.</li>
                    <li>Present analytical outputs in readable tables and charts.</li>
                    <li>Support a smooth and professional project presentation.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Technology Stack")
    st.markdown(
        """
        <span class="about-badge">Streamlit Frontend</span>
        <span class="about-badge">Python Backend</span>
        <span class="about-badge">Plotly Visualizations</span>
        <span class="about-badge">Pandas Data Handling</span>
        <span class="about-badge">igraph Theme</span>
        """,
        unsafe_allow_html=True,
    )

    meta_cols = st.columns(4)
    meta_cols[0].metric("Learner", person)
    meta_cols[1].metric("Records", overview.get("rows", "N/A"))
    meta_cols[2].metric("Variables", len(variables))
    meta_cols[3].metric("Backend Mode", backend_mode)

    with st.expander("Project Metadata"):
        st.json(project)

    st.markdown("#### Runtime Status")
    status = "Direct Python import"
    if backend_mode == "FastAPI server":
        ok, message = ensure_api_health(api_port)
        status = f"FastAPI on port {api_port}: {message}"
        if ok:
            st.success(status)
        else:
            st.warning(status)
    else:
        st.info(status)

    st.markdown('<div class="command-box">streamlit run app.py</div>', unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        """
        <div class="app-footer">
            Developed by <strong>Kashif Akram</strong> (Final Year Project)
        </div>
        """,
        unsafe_allow_html=True,
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

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Section",
            [NAV_OVERVIEW, NAV_NETWORK, NAV_ANALYTICS, NAV_DATA, NAV_RESULTS, NAV_ABOUT],
            label_visibility="collapsed",
        )
        st.divider()
        with st.expander("Advanced settings"):
            backend_mode = st.selectbox("Backend connection", ["Direct Python import", "FastAPI server"])
            api_port = st.number_input("API port", min_value=1, max_value=65535, value=DEFAULT_API_PORT, step=1)
            if backend_mode == "FastAPI server":
                ok, message = ensure_api_health(int(api_port))
                if ok:
                    st.success(message)
                else:
                    st.warning(message)

    if dashboard is None:
        st.title(APP_TITLE)
        st.error(f"Dashboard artifact not found: `{DASHBOARD_PATH}`")
        st.info("Run `python backend/run_var_pipeline.py`, then start this app again with `streamlit run app.py`.")
        return

    render_header(dashboard)
    st.divider()

    if page == NAV_OVERVIEW:
        render_metric_cards(dashboard)
        st.subheader("Overview")
        st.markdown(
            """
            This Final Year Project dashboard presents collaborative learning network
            analytics through a clean and interactive interface. It enables structured
            data exploration, graph-based network analysis, and systematic presentation
            of analytical insights and findings.
            """
        )
    elif page == NAV_NETWORK:
        render_data_preview(dashboard, title="Network Visualization")
    elif page == NAV_ANALYTICS:
        render_model_insights(dashboard)
    elif page == NAV_DATA:
        render_data_preview(dashboard, title="Data Explorer")
    elif page == NAV_RESULTS:
        render_prediction_form(dashboard, backend_mode, int(api_port))
    else:
        render_about(dashboard, backend_mode, int(api_port))

    render_footer()


if __name__ == "__main__":
    main()
