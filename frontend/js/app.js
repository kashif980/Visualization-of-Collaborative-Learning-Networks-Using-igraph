const DASHBOARD_URL = "../outputs/backend/dashboard.json";
const API_PORT = (typeof window !== "undefined" && window.FYP_API_PORT) || 9620;
const API_BASE = `http://127.0.0.1:${API_PORT}`;

let dashboardData = null;
let manualRequestSeq = 0;

document.addEventListener("DOMContentLoaded", () => initializeDashboard());

async function initializeDashboard() {
    setStatus("Loading dashboard.json...");
    try {
        const response = await fetch(DASHBOARD_URL, { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        dashboardData = await response.json();
        document.getElementById("generatedAt").textContent =
            `Generated: ${dashboardData.project?.generated_at || dashboardData.project?.status || "scaffold"}`;
        buildManualForm();
        setStatus("Dashboard loaded. Submit the form to call /predict.");
    } catch (error) {
        console.error(error);
        setStatus(`Backend output missing. Run \`run/run_pipeline.ps1\` then refresh. (${error.message})`);
    }
}

function buildManualForm() {
    const form = document.getElementById("manualForm");
    form.innerHTML = "";
    const fields = (dashboardData.manual_demo && dashboardData.manual_demo.field_schema) || [];
    if (!fields.length) {
        form.innerHTML = "<p>No input schema yet. Implement the pipeline to populate <code>manual_demo.field_schema</code>.</p>";
        return;
    }
    for (const field of fields) {
        const wrapper = document.createElement("div");
        wrapper.className = "input-field";
        wrapper.innerHTML = `
            <label for="field-${field.name}">${field.label || field.name}</label>
            <input id="field-${field.name}" name="${field.name}" type="number"
                step="${field.step ?? 'any'}"
                min="${field.min ?? ''}" max="${field.max ?? ''}"
                value="${field.default ?? 0}">
            <small>${field.description || ""}</small>
        `;
        form.appendChild(wrapper);
    }
    const submit = document.createElement("button");
    submit.type = "submit";
    submit.textContent = "Run Prediction";
    form.appendChild(submit);
    form.addEventListener("submit", (event) => { event.preventDefault(); runManualPrediction(); });
}

async function runManualPrediction() {
    const summary = document.getElementById("manualSummary");
    const values = {};
    for (const field of dashboardData.manual_demo.field_schema) {
        values[field.name] = Number(document.getElementById(`field-${field.name}`).value || 0);
    }
    const requestId = ++manualRequestSeq;
    summary.innerHTML = "<em>Contacting backend API...</em>";
    let payload;
    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ values })
        });
        payload = await response.json();
        if (!response.ok) {
            summary.innerHTML = `<strong>Backend error (HTTP ${response.status}).</strong><br><small>${payload.detail || payload.error || ""}</small>`;
            return;
        }
    } catch (error) {
        if (requestId !== manualRequestSeq) return;
        summary.innerHTML = `<strong>Backend unreachable.</strong> Start <code>run/run_backend.ps1</code> (port ${API_PORT}).<br><small>${error.message}</small>`;
        return;
    }
    if (requestId !== manualRequestSeq) return;
    summary.innerHTML = `<pre>${JSON.stringify(payload.prediction || payload, null, 2)}</pre><small>Served by FastAPI on :${API_PORT}</small>`;
}

function setStatus(message) {
    const el = document.getElementById("statusMessage");
    if (el) el.textContent = message;
}
