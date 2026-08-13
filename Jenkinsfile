pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'prudvik2026/devops-backend'
    }

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

                sh '''
                    docker build \
                      -t ${DOCKER_IMAGE}:test \
                      .
                '''
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
                      ${DOCKER_IMAGE}:test
                '''

                echo '===== Waiting for Application ====='

                sh 'sleep 5'

                echo '===== Testing Health Endpoint ====='

                sh '''
                    curl -f http://127.0.0.1:5000/health
                '''
            }

            post {
                always {
                    echo '===== Cleaning Test Container ====='

                    sh '''
                        docker rm -f devops-backend-test 2>/dev/null || true
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                echo '===== Pushing Docker Image to Docker Hub ====='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login \
                          --username "$DOCKER_USERNAME" \
                          --password-stdin

                        docker tag \
                          ${DOCKER_IMAGE}:test \
                          ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        docker tag \
                          ${DOCKER_IMAGE}:test \
                          ${DOCKER_IMAGE}:latest

                        docker push \
                          ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        docker push \
                          ${DOCKER_IMAGE}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '===== Deploying Docker Hub Image ====='

                sh '''
                    docker compose down

                    docker compose pull

                    docker compose up -d
                '''
            }
        }

        stage('Deployment Health Check') {
            steps {
                echo '===== Waiting for Deployment ====='

                sh 'sleep 10'

                echo '===== Checking Deployment ====='

                sh '''
                    docker compose ps
                '''

                echo '===== Testing Production Health Endpoint ====='

                sh '''
                    curl -f http://127.0.0.1:8080/health
                '''
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
