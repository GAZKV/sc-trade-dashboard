# sc-trade-dashboard
Open-source Python dashboard built with **FastAPI** to parse Star Citizen logs and visualize trading activity, profits, and commodity trends in real time.

Launch the backend as a FastAPI application with `uvicorn app.web.main:app`. It ingests your logs\Session files, computes buy/sell metrics, route profitability, and commodity price evolution with pandas; the frontend (Plotly/Dash) renders live charts, tables, and KPIs so haulers and miners can spot the most lucrative loops at a glance. Fully containerized, cross-platform, and ready for self-hosting

## Getting Started

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Run the API locally
Set the `LOG_ROOT` environment variable to your Star Citizen installation path:
```bash
LOG_ROOT="/path/to/StarCitizen/LIVE" uvicorn app.web.main:app --reload
```
If not set, the application defaults to `~/StarCitizen/LIVE`. On Linux and macOS
the logs may reside under your home directory (for example
`~/Library/Application Support/StarCitizen/LIVE`), so adjust `LOG_ROOT`
accordingly.

3. Generate an HTML report from logs
```bash
python scripts/generate_report.py path/to/logs/*.log report.html
```

## Sample Data

This repository includes a `sample-data/` directory containing several Star Citizen
log files. You can use these logs to try out the parsing and reporting pipeline
without collecting your own data:

```bash
python scripts/generate_report.py sample-data/*.log report.html
```

## Resource Name Mapping

The dashboard replaces raw `resourceGUID` values with human‑readable names. A
small dictionary of common mappings is bundled in `static/main.js`. When an
unknown GUID appears in the **Pending Inventory** table, a text box and `Apply`
button let you provide a custom name. The mapping is stored in your browser's
`localStorage` and applied to all tables immediately.

## Running Tests

Install the dependencies and run `pytest` to execute the test suite which
processes a few bundled log files:

```bash
pip install -r requirements.txt
pytest -q
```

## Running the Live Dashboard

1. Install the requirements and set the `LOG_ROOT` environment variable to the path of your Star Citizen `LIVE` folder:
   ```bash
   pip install -r requirements.txt
   export LOG_ROOT="/path/to/StarCitizen/LIVE"
   ```
2. Launch the FastAPI server with `uvicorn`:
   ```bash
   uvicorn app.web.main:app --reload
   ```
3. Open [http://localhost:8000](http://localhost:8000) in your browser to see real-time trading data.

When new log lines are written, the server broadcasts updates over WebSockets so the tables and charts refresh automatically without a page reload.
