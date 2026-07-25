# README Claims Audit

This audit compares the public README with the files present in the repository.
It does not certify the application for production use, security, performance,
or commercial outcomes.

## Classification

| Claim | Status | Evidence and qualification |
|---|---|---|
| The repository is a building-energy optimization portfolio project | Verified | The repository contains Python optimization code, sample-data generators, API examples, dashboards, and tests. |
| Random Forest, XGBoost, and LightGBM are represented in the optimizer | Verified | The optimizer selects these estimators and the dependency files include the corresponding libraries. |
| Synthetic building-energy data can be generated | Verified | Data-generation utilities and tests use generated input data. |
| The repository contains FastAPI endpoints for optimization workflows | Verified | `api/main.py` and `backend/main.py` define FastAPI applications and optimization-related endpoints. |
| The repository contains dashboard implementations | Verified | A Streamlit dashboard and Next.js source files are present. |
| The documented full-stack application starts with the original Docker Compose command | Unsupported | Compose references missing paths and components, including `backend/sql/init.sql`, Alembic files, frontend package metadata, Celery modules, and Docker build stages that cannot be verified from the repository. |
| The Next.js frontend can be installed and built as documented | Unsupported | Frontend source files exist, but `frontend/package.json` is absent. |
| PostgreSQL and Redis are integrated into the running application | Partially verified | Compose and dependency files declare both services, but the checked-in application does not provide a reproducible end-to-end path demonstrating the integration. |
| Celery workers and scheduled ML training are operational | Unsupported | Compose declares worker services, but the referenced task modules are absent. |
| Prometheus, Grafana, and Alertmanager are available | Partially verified | Configuration files and optional Compose services exist; an end-to-end validated monitoring setup is not demonstrated. |
| JWT authentication and role-based access control are implemented | Partially verified | Security helper code and authentication dependencies exist, but the README's complete multi-user workflow is not demonstrated end to end. |
| Multi-factor authentication is implemented | Unsupported | No complete TOTP or SMS MFA implementation was found. |
| Sensitive data uses AES-256 encryption | Unsupported | Cryptographic dependencies exist, but no verifiable application-level AES-256 data-encryption workflow was found. |
| Comprehensive audit logging is implemented | Unsupported | Application logging exists, but a verifiable persistent audit-log subsystem was not found. |
| WebSocket-based real-time monitoring is operational | Unsupported | WebSocket dependencies and configuration references exist, but a complete WebSocket application flow was not found. |
| The system provides 15–35% energy savings | Illustrative only | Optimizer suggestions use fixed heuristic percentages. They are not validated savings from real deployments. |
| The system reduces CO2 emissions by up to 25% | Unsupported | No reproducible study or implementation evidence supports this figure. |
| Return on investment is 6–18 months | Unsupported | No economic model or validated deployment data supports this range. |
| Test coverage is 95% | Unsupported | The badge is static and no committed coverage report or CI threshold demonstrates 95% coverage. |
| API response time is 156 ms | Illustrative only | The value is presented as a target/example; no reproducible benchmark artifact establishes it. |
| Dashboard load time is 687 ms | Illustrative only | No reproducible frontend build or benchmark establishes it. |
| ML prediction time is 73 ms | Illustrative only | No reproducible benchmark artifact establishes it across a defined environment. |
| Uptime is 99.97% | Illustrative only | No production monitoring history or service-level report supports this value. |
| The application is production-ready or enterprise-ready | Unsupported | Missing build inputs, incomplete service wiring, development credentials, and unverified operational claims prevent this characterization. |
| CI proves the complete application works | Partially verified | A workflow exists, but its checks do not establish the complete architecture or the public quantitative claims. |

## Documentation decisions

The revised README:

- identifies the repository as a portfolio/demo project;
- documents only components present in the repository;
- treats generated savings estimates as illustrative heuristics;
- removes production, enterprise, uptime, ROI, coverage, benchmark, and security
  claims that are not reproducibly supported;
- avoids Docker and frontend commands that reference missing files;
- recommends the directly verifiable Python setup as the primary evaluation path.

## Windows checkout compatibility

The following NTFS alternate-data-stream metadata files are tracked as ordinary
Git paths and prevent a normal checkout on Windows:

- `.flake8:Zone.Identifier`
- `docs/api/optimizer.md:Zone.Identifier`
- `examples/basic_usage.py:Zone.Identifier`
- `src/__init__.py:Zone.Identifier`
- `tests/test_optimizer.py:Zone.Identifier`
- `trained_model.joblib:Zone.Identifier`

They should be removed in a separate maintenance change from Linux or WSL:

```bash
git rm -- \
  '.flake8:Zone.Identifier' \
  'docs/api/optimizer.md:Zone.Identifier' \
  'examples/basic_usage.py:Zone.Identifier' \
  'src/__init__.py:Zone.Identifier' \
  'tests/test_optimizer.py:Zone.Identifier' \
  'trained_model.joblib:Zone.Identifier'
printf '\n*:Zone.Identifier\n' >> .gitignore
git add .gitignore
git commit -m "chore: remove tracked Zone.Identifier metadata"
```

Before that future commit, inspect `.gitignore` to avoid adding a duplicate
pattern. This cleanup is intentionally not part of the current documentation
change.
