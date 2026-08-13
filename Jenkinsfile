pipeline {
    agent any

    stages {

        stage('Test') {
            steps {
                echo '===== Running Application Test ====='
                sh 'python3 --version'
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Docker Build') {
            steps {
                echo '===== Building Docker Image ====='
                sh 'docker compose build'
            }
        }

    }

    post {
        success {
            echo '===== PIPELINE SUCCESS ====='
        }

        failure {
            echo '===== PIPELINE FAILED ====='
        }
    }
}
