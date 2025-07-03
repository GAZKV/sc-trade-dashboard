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
