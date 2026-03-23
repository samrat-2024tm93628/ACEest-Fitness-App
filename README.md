# ACEest Fitness & Gym CI/CD Pipeline

## Automated Lifecycle & Rollback Strategy
This repository follows a professional DevOps lifecycle using **GitHub Actions** for primary CI and **Jenkins** for secondary build validation.

### Version History & Tags
* **v0.1**: Initial legacy Tkinter baseline.
* **v1.1.2**: Migration to Flask with CSV Export.
* **v2.2.4**: Integration of SQLite for persistent data storage.
* **v3.2.4**: Advanced reporting and gym capacity metrics.

### Pipeline Reliability & Rollback Proof
During development, the branch `bug/failed-logic-test` was used to verify the "Quality Gate". 
* **Detection**: The faulty BMI logic triggered a failure in the **Pytest** suite during the **GitHub Actions** run.
* **Auto-Rollback**: Because the build failed, the Docker image was never assembled. The production environment remained securely on the last stable tag (**v3.2.4**).

---

## VCS Maturity & Automated Rollback Strategy
This project implements a rigorous lifecycle to guarantee code integrity and environmental consistency.

### Branching & Versioning Strategy
| Branch Type | Purpose                                                 | Example                          |
|-------------|---------------------------------------------------------|----------------------------------|
| `main`      | Stable, production-ready code only                      | Tags `v1.0`, `v2.2.4`, `v3.2.4`  |
| `feature/*` | Modular development of new features                     | `feature/v2-db-integration`      |
| `bug/*`     | Testing "Quality Gates" without compromising production | `bug/failed-logic-test`          |

### Automated Quality Gates & Rollback
* **Primary Gate (GitHub Actions)**: Every push to any branch triggers an automated suite that performs linting and unit testing via **Pytest**.
* **Secondary Validation (Jenkins)**: Acts as the final build environment for the `main` branch, ensuring a clean build before any deployment signal.

### Rollback Logic
If a failure is detected in the `bug/failed-logic-test` branch, the pipeline stops immediately. Because the **Docker Image Assembly** step is conditional on a successful test phase (`if: success()`), no faulty image is ever created. The live environment remains securely pointed at the last successful Git Tag, effectively **automating the rollback process**.


## Local Setup & Execution

### Prerequisites
- Python 3.9+
- pip
- Docker (optional, for container testing)

### 1. Clone the Repository
```bash
git clone https://github.com/samrat-2024tm93628/ACEest-Fitness-App.git
cd ACEest-Fitness-App
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
The API will be available at `http://localhost:5000`.

### 4. Available API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/programs` | List all fitness programs |
| POST | `/calculate` | Calculate BMI (`weight`, `height` in JSON body) |
| GET | `/export/csv` | Download fitness plans as CSV |
| POST | `/client` | Save client name & BMI to SQLite |
| GET | `/status` | Gym capacity & peak-hour metrics |

---

## Running Tests Manually

### Run the Full Pytest Suite
```bash
pytest test_app.py
```

### Run with Verbose Output (recommended)
```bash
pytest test_app.py -v
```

### Run by Route Group
```bash
# Health check tests
pytest test_app.py -v -k "health"

# Programs tests
pytest test_app.py -v -k "programs"

# BMI calculation tests (includes edge cases)
pytest test_app.py -v -k "bmi"

# CSV export tests
pytest test_app.py -v -k "csv"

# Client persistence tests
pytest test_app.py -v -k "client"

# Gym status tests
pytest test_app.py -v -k "status"
```

### Syntax / Lint Check (mirrors CI)
```bash
python -m compileall .
```

### Test Coverage Summary
The test suite contains **20 test cases** across all 6 API endpoints:

| # | Test Name | Route | Type |
|---|-----------|-------|------|
| 1 | `test_health_check` | `GET /health` | Status + fields |
| 2 | `test_get_all_programs_status` | `GET /programs` | Status |
| 3 | `test_get_all_programs_content` | `GET /programs` | All 3 programs present |
| 4 | `test_programs_have_required_fields` | `GET /programs` | Schema validation |
| 5 | `test_bmi_calculation` | `POST /calculate` | Correct BMI value |
| 6 | `test_bmi_response_has_message` | `POST /calculate` | Field presence |
| 7 | `test_bmi_missing_payload_returns_400` | `POST /calculate` | Edge case |
| 8 | `test_bmi_missing_weight_returns_400` | `POST /calculate` | Edge case |
| 9 | `test_bmi_missing_height_returns_400` | `POST /calculate` | Edge case |
| 10 | `test_bmi_no_json_returns_400` | `POST /calculate` | Edge case |
| 11 | `test_export_csv_status` | `GET /export/csv` | Status |
| 12 | `test_export_csv_content_type` | `GET /export/csv` | `text/csv` MIME type |
| 13 | `test_export_csv_has_header_row` | `GET /export/csv` | CSV structure |
| 14 | `test_export_csv_has_program_data` | `GET /export/csv` | Data integrity |
| 15 | `test_save_client_status` | `POST /client` | Status 201 |
| 16 | `test_save_client_response_message` | `POST /client` | Confirmation message |
| 17 | `test_gym_status_returns_200` | `GET /status` | Status |
| 18 | `test_gym_status_has_capacity` | `GET /status` | Capacity is int |
| 19 | `test_gym_status_has_required_fields` | `GET /status` | All metric fields |

---

## CI/CD Integration Overview

This project uses a **dual-pipeline** strategy — GitHub Actions for cloud-based CI on every branch, and Jenkins for local/secondary build validation on `main`.

### GitHub Actions (Primary Gate)
**File:** `.github/workflows/main.yml`

```
Push to ANY branch
       │
       ▼
┌─────────────────────────┐
│  1. Checkout Code        │
│  2. Set up Python 3.9    │
│  3. Install Dependencies │
│  4. Build & Lint         │  ← python -m compileall .
│  5. Automated Testing    │  ← pytest test_app.py
│  6. Docker Image Assembly│  ← Only on `main` + success()
└─────────────────────────┘
```

- Triggered on **every push** to any branch (catches bugs early on feature/bug branches).
- Pull Requests to `main` also trigger the full suite.
- The **Docker Image Assembly** step is gated with `if: github.ref == 'refs/heads/main' && success()` — a failing test on any branch **prevents** a faulty image from ever being built.

### Jenkins (Secondary Validation)
**File:** `Jenkinsfile`

```
main branch (local Jenkins server)
       │
       ▼
┌──────────────────────────────────┐
│  Stage 1: Checkout               │  ← checkout scm
│  Stage 2: Clean Build            │  ← python -m venv + pip install
│  Stage 3: Quality Gate (Pytest)  │  ← pytest test_app.py
└──────────────────────────────────┘
```

- Configured to run on a **Windows agent**, using `bat` commands and a virtual environment (`venv`).
- Acts as the **final validation layer** before any deployment signal is issued, independent of the GitHub Actions environment.

### Rollback Flow
```
Bug branch fails Pytest (GitHub Actions)
       │
       ▼
Docker step is SKIPPED (conditional gate)
       │
       ▼
Production remains on last stable Git Tag (e.g., v3.2.4)
       │
       ▼
Fix is committed → merge to main → all gates pass → new tag released
```