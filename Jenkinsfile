// Jenkinsfile
//
// Requires on the agent: python3 (with venv module) and docker.
// Assumes a standard freestyle/multibranch pipeline job pointed at this repo.

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        VENV_DIR      = '.venv'
        IMAGE_NAME    = 'diabetes-mlops-api'
        IMAGE_TAG     = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up virtualenv') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    ruff check .
                '''
            }
        }

        stage('Train model') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python train.py
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        // Uncomment and configure once a registry + Jenkins credentials
        // (e.g. a "dockerhub-creds" or ECR credential) are set up.
        //
        // stage('Push Docker image') {
        //     steps {
        //         withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
        //                                            usernameVariable: 'DOCKER_USER',
        //                                            passwordVariable: 'DOCKER_PASS')]) {
        //             sh '''
        //                 echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
        //                 docker tag ${IMAGE_NAME}:${IMAGE_TAG} $DOCKER_USER/${IMAGE_NAME}:${IMAGE_TAG}
        //                 docker push $DOCKER_USER/${IMAGE_NAME}:${IMAGE_TAG}
        //             '''
        //         }
        //     }
        // }
    }

    post {
        success {
            archiveArtifacts artifacts: 'models/diabetes_model.pkl, models/metadata.json', fingerprint: true
        }
        always {
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}
