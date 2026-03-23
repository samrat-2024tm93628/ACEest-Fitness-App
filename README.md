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


## Local Execution
1. Install requirements: `pip install -r requirements.txt`
2. Run app: `python app.py`
3. Run tests: `pytest test_app.py`