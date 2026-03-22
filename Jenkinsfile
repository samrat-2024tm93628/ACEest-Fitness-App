pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                // Pull code from the GitHub Repository [cite: 19]
                checkout scm
            }
        }
        stage('Clean Build') {
            steps {
                // Ensure the environment compiles correctly [cite: 19]
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Quality Gate') {
            steps {
                // Perform secondary validation [cite: 20]
                sh 'pytest test_app.py'
            }
        }
    }
}