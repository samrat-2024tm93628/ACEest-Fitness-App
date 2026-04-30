// ACEest Fitness — full CI/CD pipeline
// Cross-platform (Linux/Mac agents use sh, Windows agents use bat).
// Stages that depend on external systems (SonarQube, Docker registry,
// Kubernetes) are gated so the pipeline still completes end-to-end on a
// minimally-configured Jenkins. Configure these in Jenkins to enable them:
//   - SonarQube installation named "SonarQube" (Manage Jenkins -> System)
//   - Credentials id "dockerhub-creds" (username/password)
//   - Credentials id "kubeconfig" (secret file containing kubeconfig)
//   - Env var DOCKER_REGISTRY (e.g. docker.io/<user>) and IMAGE_NAME

pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME      = "${env.IMAGE_NAME ?: 'aceest-fitness'}"
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = "${env.DOCKER_REGISTRY ?: ''}"   // e.g. docker.io/yourname
        K8S_NAMESPACE   = "aceest"
        K8S_DEPLOYMENT  = "aceest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements-dev.txt
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            pip install --upgrade pip
                            pip install -r requirements-dev.txt
                        '''
                    }
                }
            }
        }

        stage('Lint') {
            steps {
                script {
                    if (isUnix()) {
                        sh '. venv/bin/activate && python -m compileall app.py test_app.py'
                    } else {
                        bat 'call venv\\Scripts\\activate.bat && python -m compileall app.py test_app.py'
                    }
                }
            }
        }

        stage('Test + Coverage') {
            steps {
                script {
                    if (isUnix()) {
                        sh '. venv/bin/activate && pytest --junitxml=pytest-report.xml'
                    } else {
                        bat 'call venv\\Scripts\\activate.bat && pytest --junitxml=pytest-report.xml'
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'pytest-report.xml'
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true, fingerprint: true
                }
            }
        }

/*
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    script {
                        if (isUnix()) {
                            sh 'sonar-scanner'
                        } else {
                            bat 'sonar-scanner.bat'
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
*/

        stage('Docker Build') {
            steps {
                script {
                    def fullImage = env.DOCKER_REGISTRY ? "${env.DOCKER_REGISTRY}/${env.IMAGE_NAME}" : env.IMAGE_NAME
                    env.FULL_IMAGE = fullImage
                    if (isUnix()) {
                        sh "docker build -t ${fullImage}:${IMAGE_TAG} -t ${fullImage}:latest ."
                    } else {
                        bat "docker build -t ${fullImage}:${IMAGE_TAG} -t ${fullImage}:latest ."
                    }
                }
            }
        }

/*
        stage('Docker Push') {
            when {
                allOf {
                    branch 'main'
                    expression { return env.DOCKER_REGISTRY?.trim() }
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                                docker push ''' + "${env.FULL_IMAGE}:${IMAGE_TAG}" + '''
                                docker push ''' + "${env.FULL_IMAGE}:latest" + '''
                            '''
                        } else {
                            bat """
                                echo %DOCKER_PASS%| docker login -u %DOCKER_USER% --password-stdin
                                docker push ${env.FULL_IMAGE}:${IMAGE_TAG}
                                docker push ${env.FULL_IMAGE}:latest
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                allOf {
                    branch 'main'
                    expression { return fileExists('k8s/deployment.yaml') }
                }
            }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    script {
                        def img = "${env.FULL_IMAGE}:${IMAGE_TAG}"
                        if (isUnix()) {
                            sh """
                                kubectl apply -f k8s/ -n ${K8S_NAMESPACE}
                                kubectl set image deployment/${K8S_DEPLOYMENT} app=${img} -n ${K8S_NAMESPACE} --record
                                kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} --timeout=2m
                            """
                        } else {
                            bat """
                                kubectl apply -f k8s/ -n ${K8S_NAMESPACE}
                                kubectl set image deployment/${K8S_DEPLOYMENT} app=${img} -n ${K8S_NAMESPACE} --record
                                kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} --timeout=2m
                            """
                        }
                    }
                }
            }
        }
*/

/*
        stage('Smoke Test') {
            when {
                expression { return env.SMOKE_BASE_URL?.trim() }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . venv/bin/activate
                            BASE_URL=${env.SMOKE_BASE_URL} pytest -m smoke --no-cov
                        """
                    } else {
                        bat """
                            call venv\\Scripts\\activate.bat
                            set BASE_URL=${env.SMOKE_BASE_URL}
                            pytest -m smoke --no-cov
                        """
                    }
                }
            }
        }
*/
    }

    post {
        success {
            echo "Build #${BUILD_NUMBER} succeeded. Image: ${env.FULL_IMAGE ?: env.IMAGE_NAME}:${IMAGE_TAG}"
        }
/*
        failure {
            echo "Build #${BUILD_NUMBER} failed. Attempting rollback if a deployment exists."
            script {
                if (fileExists('k8s/deployment.yaml')) {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        if (isUnix()) {
                            sh """
                                kubectl rollout undo deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} || true
                                kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} --timeout=2m || true
                            """
                        } else {
                            bat """
                                kubectl rollout undo deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} || ver > nul
                                kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE} --timeout=2m || ver > nul
                            """
                        }
                    }
                }
            }
        }
*/
        always {
            cleanWs(deleteDirs: true, notFailBuild: true,
                patterns: [[pattern: 'venv/**', type: 'INCLUDE'],
                           [pattern: '.pytest_cache/**', type: 'INCLUDE']])
        }
    }
}
