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
                        -t ${DOCKER_IMAGE}:test .
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

                        echo "===== Tagging Docker Images ====="

                        docker tag \
                            ${DOCKER_IMAGE}:test \
                            ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        docker tag \
                            ${DOCKER_IMAGE}:test \
                            ${DOCKER_IMAGE}:latest

                        echo "===== Pushing Build ${BUILD_NUMBER} ====="

                        docker push \
                            ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        echo "===== Pushing Latest Image ====="

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
                    echo "===== Stopping Existing Deployment ====="

                    docker compose down

                    echo "===== Pulling Latest Docker Hub Images ====="

                    docker compose pull

                    echo "===== Starting Application ====="

                    docker compose up -d
                '''
            }
        }

        stage('Deployment Health Check') {
            steps {
                echo '===== Verifying Production Deployment ====='

                sh '''
                    echo "===== Current Containers ====="

                    docker compose ps

                    echo "===== Waiting for Backend Health ====="

                    for i in 1 2 3 4 5 6
                    do
                        echo "Health check attempt $i/6"

                        if curl -fsS http://127.0.0.1:8080/health
                        then
                            echo ""
                            echo "===== BACKEND HEALTH CHECK PASSED ====="
                            exit 0
                        fi

                        echo "Backend is not ready yet..."
                        sleep 5
                    done

                    echo "===== BACKEND HEALTH CHECK FAILED ====="

                    echo "===== Docker Compose Status ====="

                    docker compose ps

                    echo "===== Backend Logs ====="

                    docker compose logs --tail=50 backend

                    echo "===== Database Logs ====="

                    docker compose logs --tail=50 db

                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo '========================================='
            echo '===== PIPELINE SUCCESS ====='
            echo '========================================='
            echo "Docker Image: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
            echo "Docker Image: ${DOCKER_IMAGE}:latest"
        }

        failure {
            echo '========================================='
            echo '===== PIPELINE FAILED ====='
            echo '========================================='
        }

        always {
            echo '===== Pipeline Execution Completed ====='
        }
    }
}
