pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                // Pulls code from GitHub
                checkout scm
            }
        }
        stage('Clean Build') {
            steps {
                // On Windows, use 'bat' instead of 'sh'
                // Also, Windows usually just uses 'python' instead of 'python3'
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\activate && pip install -r requirements.txt'
            }
        }
        stage('Quality Gate') {
            steps {
                // Run tests using the Windows virtual env path
                bat 'venv\\Scripts\\activate && pytest test_app.py'
            }
        }
    }
}