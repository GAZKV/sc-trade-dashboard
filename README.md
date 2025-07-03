# sc-trade-dashboard
Open-source Python web dashboard that parses Star Citizen logs to visualize trading activity, profits, and commodity trends in real time.

A lightweight, Flask-powered web app that turns raw Star Citizen log files into an interactive trading dashboard.
The backend ingests your logs\Session files, computes buy/sell metrics, route profitability, and commodity price evolution with pandas; the frontend (Plotly/Dash) renders live charts, tables, and KPIs so haulers and miners can spot the most lucrative loops at a glance. Fully containerized, cross-platform, and ready for self-hosting

## Getting Started

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Run the API locally
```bash
uvicorn app.web.main:app --reload
```

## Running with Uvicorn

Launch the FastAPI server from the repository root using Uvicorn. The example below starts the
app with hot reloading enabled and binds it to all interfaces on port 8000:

```bash
uvicorn app.web.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser to see the dashboard.

3. Generate an HTML report from logs
```bash
python scripts/generate_report.py path/to/logs/*.log report.html
```

## Report Generation Examples

Generate an HTML report from the bundled sample logs:

```bash
python scripts/generate_report.py sample-data/*.log sample-report.html
```

Generate both HTML and Excel reports from an entire log directory:

```bash
python scripts/generate_report.py sample-data report.html --excel report.xlsx
```
