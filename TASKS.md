# Development Tasks

## 1. Package dependencies
- [ ] Create a `requirements.txt` listing packages: `fastapi`, `uvicorn`, `pandas`, `matplotlib`, and `jinja2`.
- [ ] Reference this file in the README for setup instructions.

## 2. Add automated tests
- [ ] Add unit tests using `pytest` for `log_parser` and `analysis` functions.
- [ ] Configure GitHub Actions or another CI to run the tests.

## 3. Improve README
- [ ] Document how to run the web application with `uvicorn`.
- [ ] Include example commands to generate reports using `scripts/generate_report.py`.

## 4. Address warnings
- [ ] Update FastAPI startup events to use lifespan handlers instead of deprecated `on_event`.

## 5. Sample data
- [ ] Provide example Star Citizen log files in a `sample-data` directory for testing and documentation.
