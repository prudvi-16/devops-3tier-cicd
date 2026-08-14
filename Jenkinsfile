pipeline {
    agent any

    environment {
        BACKEND_IMAGE = 'prudvik2026/devops-backend'
        FRONTEND_IMAGE = 'prudvik2026/devops-frontend'
        COMPOSE_PROJECT = 'devops-3tier-pipeline'
    }

    stages {

        stage('Test') {
            steps {
                echo '========================================='
                echo '===== Running Backend Application Test ====='
                echo '========================================='

                sh '''
                    set -e

                    python3 --version

                    echo "===== Compiling Backend Application ====="

                    cd backend

                    python3 -m py_compile app.py

                    echo "===== Backend Application Test PASSED ====="
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo '========================================='
                echo '===== Building Backend Docker Image ====='
                echo '========================================='

                sh '''
                    set -e

                    docker build \
                        -t ${BACKEND_IMAGE}:test \
                        backend

                    echo "===== Backend Docker Build PASSED ====="
                '''
            }
        }

        stage('Container Test') {
            steps {
                echo '========================================='
                echo '===== Testing Backend Container ====='
                echo '========================================='

                sh '''
                    set -e

                    docker rm -f devops-backend-test 2>/dev/null || true

                    docker run -d \
                        --name devops-backend-test \
                        -p 5000:5000 \
                        ${BACKEND_IMAGE}:test

                    echo "===== Waiting for Backend ====="

                    sleep 5

                    echo "===== Testing Backend Health Endpoint ====="

                    curl -fsS \
                        http://127.0.0.1:5000/health

                    echo ""

                    echo "===== Backend Container Test PASSED ====="
                '''
            }

            post {
                always {
                    echo '===== Cleaning Backend Test Container ====='

                    sh '''
                        docker rm -f devops-backend-test 2>/dev/null || true
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                echo '========================================='
                echo '===== Pushing Backend Docker Image ====='
                echo '========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "===== Tagging Backend Images ====="

                        docker tag \
                            ${BACKEND_IMAGE}:test \
                            ${BACKEND_IMAGE}:${BUILD_NUMBER}

                        docker tag \
                            ${BACKEND_IMAGE}:test \
                            ${BACKEND_IMAGE}:latest

                        echo "===== Pushing Backend Build ${BUILD_NUMBER} ====="

                        docker push \
                            ${BACKEND_IMAGE}:${BUILD_NUMBER}

                        echo "===== Pushing Backend Latest ====="

                        docker push \
                            ${BACKEND_IMAGE}:latest

                        docker logout

                        echo "===== Backend Docker Push PASSED ====="
                    '''
                }
            }
        }

        stage('Frontend Test') {
            steps {
                echo '========================================='
                echo '===== Running Frontend Test ====='
                echo '========================================='

                sh '''
                    set -e

                    echo "===== Checking Frontend Files ====="

                    test -f frontend/index.html
                    test -f frontend/style.css
                    test -f frontend/script.js
                    test -f frontend/Dockerfile

                    echo "===== Checking Frontend HTML ====="

                    grep -q "DevOps Employee Portal" frontend/index.html

                    echo "===== Checking Frontend JavaScript ====="

                    grep -q "window.location.hostname" frontend/script.js
                    grep -q ":8080" frontend/script.js

                    echo "===== Frontend Test PASSED ====="
                '''
            }
        }

        stage('Frontend Docker Build') {
            steps {
                echo '========================================='
                echo '===== Building Frontend Docker Image ====='
                echo '========================================='

                sh '''
                    set -e

                    docker build \
                        -t ${FRONTEND_IMAGE}:test \
                        frontend

                    echo "===== Frontend Docker Build PASSED ====="
                '''
            }
        }

        stage('Frontend Container Test') {
            steps {
                echo '========================================='
                echo '===== Testing Frontend Container ====='
                echo '========================================='

                sh '''
                    set -e

                    docker rm -f devops-frontend-ci-test 2>/dev/null || true

                    docker run -d \
                        --name devops-frontend-ci-test \
                        -p 8088:80 \
                        ${FRONTEND_IMAGE}:test

                    echo "===== Waiting for Nginx ====="

                    sleep 3

                    echo "===== Testing Frontend HTTP ====="

                    curl -fsS \
                        http://127.0.0.1:8088/ \
                        > /tmp/frontend.html

                    grep -q "DevOps Employee Portal" /tmp/frontend.html

                    echo "===== Testing Frontend JavaScript ====="

                    curl -fsS \
                        http://127.0.0.1:8088/script.js \
                        | grep -q "window.location.hostname"

                    echo "===== Frontend Container Test PASSED ====="
                '''
            }

            post {
                always {
                    echo '===== Cleaning Frontend Test Container ====='

                    sh '''
                        docker rm -f devops-frontend-ci-test 2>/dev/null || true
                        rm -f /tmp/frontend.html
                    '''
                }
            }
        }

        stage('Frontend Docker Push') {
            steps {
                echo '========================================='
                echo '===== Pushing Frontend Docker Image ====='
                echo '========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "===== Tagging Frontend Images ====="

                        docker tag \
                            ${FRONTEND_IMAGE}:test \
                            ${FRONTEND_IMAGE}:${BUILD_NUMBER}

                        docker tag \
                            ${FRONTEND_IMAGE}:test \
                            ${FRONTEND_IMAGE}:latest

                        echo "===== Pushing Frontend Build ${BUILD_NUMBER} ====="

                        docker push \
                            ${FRONTEND_IMAGE}:${BUILD_NUMBER}

                        echo "===== Pushing Frontend Latest ====="

                        docker push \
                            ${FRONTEND_IMAGE}:latest

                        docker logout

                        echo "===== Frontend Docker Push PASSED ====="
                    '''
                }
            }
        }

        stage('Prepare Environment') {
            steps {
                echo '========================================='
                echo '===== Preparing Deployment Environment ====='
                echo '========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'db-credentials',
                        usernameVariable: 'POSTGRES_USER_SECRET',
                        passwordVariable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Creating Temporary Environment File ====="

                        cat > backend/.env <<ENVEOF
POSTGRES_DB=employee_db
POSTGRES_USER=${POSTGRES_USER_SECRET}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
ENVEOF

                        chmod 600 backend/.env

                        echo "===== Environment File Created ====="

                        echo "POSTGRES_DB=employee_db"
                        echo "POSTGRES_USER=${POSTGRES_USER_SECRET}"
                        echo "POSTGRES_PASSWORD=********"

                        echo "===== Validating Compose Configuration ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            config > /dev/null

                        echo "===== Compose Configuration VALID ====="
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '========================================='
                echo '===== Deploying Backend + Database ====='
                echo '========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'db-credentials',
                        usernameVariable: 'POSTGRES_USER_SECRET',
                        passwordVariable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Recreating Environment File ====="

                        cat > backend/.env <<ENVEOF
POSTGRES_DB=employee_db
POSTGRES_USER=${POSTGRES_USER_SECRET}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
ENVEOF

                        chmod 600 backend/.env

                        echo "===== Stopping Existing Backend Deployment ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            down

                        echo "===== Removing Old Test Containers ====="

                        docker rm -f devops-backend-test 2>/dev/null || true
                        docker rm -f devops-frontend-ci-test 2>/dev/null || true

                        echo "===== Pulling Latest Backend Images ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            pull

                        echo "===== Starting Backend + Database ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            up -d

                        echo "===== Pulling Latest Frontend Image ====="

                        docker pull ${FRONTEND_IMAGE}:latest

                        echo "===== Stopping Existing Frontend ====="

                        docker rm -f ${COMPOSE_PROJECT}-frontend 2>/dev/null || true
                        docker rm -f devops-frontend 2>/dev/null || true
                        docker rm -f devops-frontend-test 2>/dev/null || true

                        echo "===== Starting Frontend ====="

                        docker run -d \
                            --name ${COMPOSE_PROJECT}-frontend \
                            --restart unless-stopped \
                            -p 80:80 \
                            ${FRONTEND_IMAGE}:latest

                        echo "===== Backend + Database Status ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            ps

                        echo "===== Frontend Status ====="

                        docker ps \
                            --filter "name=${COMPOSE_PROJECT}-frontend" \
                            --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'

                        echo "===== Deployment Started ====="
                    '''
                }
            }
        }

        stage('Deployment Health Check') {
            steps {
                echo '========================================='
                echo '===== Production Health Check ====='
                echo '========================================='

                withCredentials([
                    usernamePassword(
                        credentialsId: 'db-credentials',
                        usernameVariable: 'POSTGRES_USER_SECRET',
                        passwordVariable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        cat > backend/.env <<ENVEOF
POSTGRES_DB=employee_db
POSTGRES_USER=${POSTGRES_USER_SECRET}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
ENVEOF

                        chmod 600 backend/.env

                        echo "===== Current Backend Containers ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            ps

                        echo "===== Waiting for Backend Health ====="

                        BACKEND_OK=false

                        for i in 1 2 3 4 5 6 7 8 9 10
                        do
                            echo "Health check attempt $i/10"

                            if curl -fsS \
                                http://127.0.0.1:8080/health
                            then
                                echo ""
                                echo "===== BACKEND HEALTH CHECK PASSED ====="
                                BACKEND_OK=true
                                break
                            fi

                            echo "Backend is not ready yet..."

                            sleep 5
                        done

                        if [ "$BACKEND_OK" != "true" ]
                        then
                            echo "===== BACKEND HEALTH CHECK FAILED ====="

                            docker compose \
                                -p ${COMPOSE_PROJECT} \
                                --env-file backend/.env \
                                -f backend/compose.yaml \
                                ps

                            docker compose \
                                -p ${COMPOSE_PROJECT} \
                                --env-file backend/.env \
                                -f backend/compose.yaml \
                                logs --tail=50 backend

                            exit 1
                        fi

                        echo "===== API CHECK ====="

                        curl -fsS \
                            http://127.0.0.1:8080/api

                        echo ""

                        echo "===== Database Status ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            ps db

                        echo "===== Frontend Status ====="

                        docker ps \
                            --filter "name=${COMPOSE_PROJECT}-frontend" \
                            --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'

                        echo "===== Frontend HTTP Check ====="

                        curl -fsS \
                            http://127.0.0.1:80/ \
                            > /tmp/frontend-production.html

                        grep -q "DevOps Employee Portal" \
                            /tmp/frontend-production.html

                        echo "===== FRONTEND HEALTH CHECK PASSED ====="

                        echo "===== Frontend JavaScript Check ====="

                        curl -fsS \
                            http://127.0.0.1:80/script.js \
                            | grep -q "window.location.hostname"

                        echo "===== FRONTEND JAVASCRIPT CHECK PASSED ====="

                        rm -f /tmp/frontend-production.html

                        echo "========================================="
                        echo "===== FULL 3-TIER DEPLOYMENT PASSED ====="
                        echo "========================================="
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '========================================='
            echo '===== PIPELINE SUCCESS ====='
            echo '========================================='

            echo "Backend Image: ${BACKEND_IMAGE}:${BUILD_NUMBER}"
            echo "Backend Image: ${BACKEND_IMAGE}:latest"

            echo "Frontend Image: ${FRONTEND_IMAGE}:${BUILD_NUMBER}"
            echo "Frontend Image: ${FRONTEND_IMAGE}:latest"

            echo '========================================='
            echo '===== APPLICATION DEPLOYED ====='
            echo '========================================='
        }

        failure {
            echo '========================================='
            echo '===== PIPELINE FAILED ====='
            echo '========================================='
        }

        always {
            echo '===== Pipeline Execution Completed ====='

            sh '''
                rm -f backend/.env 2>/dev/null || true
                rm -f /tmp/frontend.html 2>/dev/null || true
                rm -f /tmp/frontend-production.html 2>/dev/null || true
            '''
        }
    }
}
