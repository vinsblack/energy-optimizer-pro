# Energy Optimizer Pro

Energy Optimizer Pro is a portfolio and demonstration project for exploring
building-energy data, machine-learning models, optimization heuristics, APIs,
and dashboard concepts.

The repository is intended for technical evaluation and experimentation. It is
not a production energy-management service, and its generated recommendations
must not be treated as validated savings, financial projections, or operational
advice.

## What is implemented

- Python utilities for generating synthetic building-energy data
- Data preprocessing and model training with scikit-learn-compatible estimators
- Random Forest, XGBoost, and LightGBM model selection
- Prediction and rule-based optimization suggestions
- Model persistence with Joblib
- FastAPI implementations exposing demonstration optimization endpoints
- Streamlit and Next.js dashboard source code
- Unit and API test modules
- Example Docker, monitoring, and CI configuration

Some infrastructure definitions are incomplete or reference files that are not
present. See [README_CLAIMS_AUDIT.md](README_CLAIMS_AUDIT.md) for an evidence-based
review of the original documentation.

## Scope and limitations

This project works primarily with synthetic or user-supplied data. Percentages
returned by optimization suggestions are heuristic estimates encoded in the
demonstration logic; they are not measured outcomes from deployed buildings.

The repository does not provide evidence for production uptime, return on
investment, guaranteed energy savings, fixed performance figures, enterprise
readiness, or a specific test-coverage percentage.

The checked-in Docker Compose and frontend definitions are architectural
examples rather than a verified one-command deployment. In particular, the
frontend source is present without its package manifest, and some Compose
services reference modules or files that are not included.

## Repository structure

```text
api/                              FastAPI demonstration API
backend/                          Extended API experiments and requirements
dashboard/                        Streamlit dashboard
examples/                         Python usage examples
frontend/                         Next.js UI source (package manifest absent)
monitoring/                       Prometheus, Grafana, and alert examples
src/building_energy_optimizer/    Core optimizer and supporting utilities
tests/                            Optimizer and API tests
docker-compose*.yml               Infrastructure examples
```

## Local evaluation

The most direct evaluation path is the Python package and its tests.

### Prerequisites

- Python 3.11
- A virtual environment

### Setup

```bash
git clone https://github.com/vinsblack/energy-optimizer-pro.git
cd energy-optimizer-pro

python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Run the tests

```bash
pytest tests -v
```

The repository contains multiple generations of API and optimizer code. Test
results can depend on the selected Python version and dependency resolution;
review failures before relying on a specific component.

### Run an example

```bash
python examples/basic_usage.py
```

### Run the demonstration API

```bash
uvicorn api.main:app --reload
```

The OpenAPI interface is available at <http://localhost:8000/docs>.

### Run the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

## Technology represented

- **Python and data:** Python, pandas, NumPy, scikit-learn, XGBoost, LightGBM
- **Backend:** FastAPI, Pydantic, Joblib
- **UI experiments:** Streamlit and Next.js source
- **Infrastructure examples:** Docker Compose, PostgreSQL, Redis, Prometheus,
  Grafana, and Alertmanager
- **Quality tooling:** Pytest and GitHub Actions configuration

The presence of an integration or configuration file does not imply that the
complete service is production-ready or validated end to end.

## Security

The repository includes authentication helpers and security-related
dependencies, but it should not be treated as a security-reviewed application.
Example credentials and development secrets in configuration files must never be
used in a deployed environment.

No claim is made here that MFA, application-level AES-256 encryption,
production-grade RBAC, or persistent audit logging is complete.

## Data and recommendation disclaimer

Generated datasets, forecasts, recommendation percentages, and cost estimates
are illustrative. Validate models with representative data and involve qualified
energy professionals before making operational or financial decisions.

## Known repository issue

Several tracked `:Zone.Identifier` metadata files prevent a normal Windows
checkout. They are documented in the claims audit and should be removed in a
separate maintenance commit from Linux or WSL.

## License

This repository includes an MIT License. Third-party dependencies and datasets
remain subject to their own terms.
