# sc-trade-dashboard
Open-source Python web dashboard that parses Star Citizen logs to visualize trading activity, profits, and commodity trends in real time.

A lightweight, Flask-powered web app that turns raw Star Citizen log files into an interactive trading dashboard.
The backend ingests your logs\Session files, computes buy/sell metrics, route profitability, and commodity price evolution with pandas; the frontend (Plotly/Dash) renders live charts, tables, and KPIs so haulers and miners can spot the most lucrative loops at a glance. Fully containerized, cross-platform, and ready for self-hosting