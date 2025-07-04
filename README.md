# sc-trade-dashboard
Open-source Python dashboard built with **FastAPI** to parse Star Citizen logs and visualize trading activity, profits, and commodity trends in real time.

Launch the backend as a FastAPI application with `uvicorn app.web.main:app`. It ingests your logs\Session files, computes buy/sell metrics, route profitability, and commodity price evolution with pandas; the frontend uses Chart.js to render live charts, tables, and KPIs so haulers and miners can spot the most lucrative loops at a glance. Fully containerized, cross-platform, and ready for self-hosting

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
If not set, the application defaults to `~/StarCitizen/LIVE`.
On macOS the folder is typically found under
`$HOME/Library/Application Support/StarCitizen/LIVE` and on most Linux
distributions under `$HOME/.local/share/StarCitizen/LIVE`.
Set the `LOG_ROOT` environment variable to whichever location matches your
installation before starting the server.

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

1. Install the requirements and set `LOG_ROOT` to your Star Citizen `LIVE` folder:

   ```bash
   pip install -r requirements.txt
   export LOG_ROOT="/path/to/StarCitizen/LIVE"
   ```

2. Run the FastAPI server:

   ```bash
   uvicorn app.web.main:app --reload
   ```

3. Visit [http://localhost:8000](http://localhost:8000) to see real-time data.

The dashboard pushes updates over WebSockets whenever new log lines appear so charts refresh automatically.
