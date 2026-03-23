# ACEest Fitness & Gym CI/CD Pipeline

## Automated Lifecycle & Rollback Strategy
[cite_start]This repository follows a professional DevOps lifecycle using **GitHub Actions** for primary CI and **Jenkins** for secondary build validation[cite: 18, 21].

### Version History & Tags
* **v0.1**: Initial legacy Tkinter baseline.
* **v1.1.2**: Migration to Flask with CSV Export.
* **v2.2.4**: Integration of SQLite for persistent data storage.
* **v3.2.4**: Advanced reporting and gym capacity metrics.

### Pipeline Reliability & Rollback Proof
During development, the branch `bug/failed-logic-test` was used to verify the "Quality Gate". 
* **Detection**: The faulty BMI logic triggered a failure in the **Pytest** suite during the **GitHub Actions** run.
* **Auto-Rollback**: Because the build failed, the Docker image was never assembled. The production environment remained securely on the last stable tag (**v3.2.4**).

## Local Execution
1. Install requirements: `pip install -r requirements.txt`
2. Run app: `python app.py`
3. Run tests: `pytest test_app.py`