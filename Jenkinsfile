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
                sh 'docker build -t devops-backend:test .'
            }
        }

        stage('Container Test') {
            steps {
                echo '===== Starting Test Container ====='

                sh '''
                    docker rm -f devops-backend-test 2>/dev/null || true

                    docker run -d \
                      --name devops-backend-test \
                      -p 5000:5000 \
                      devops-backend:test
                '''

                echo '===== Waiting for Application ====='

                sh '''
                    sleep 5
                '''

                echo '===== Testing Health Endpoint ====='

                sh '''
                    curl -f http://127.0.0.1:5000/health
                '''
            }

            post {
                always {
                    echo '===== Cleaning Test Container ====='
                    sh 'docker rm -f devops-backend-test 2>/dev/null || true'
                }
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
