pipeline {

    agent any

    environment {
        BACKEND_IMAGE  = "prudvik2026/devops-backend"
        FRONTEND_IMAGE = "prudvik2026/devops-frontend"

        COMPOSE_PROJECT = "devops-3tier-pipeline"
        COMPOSE_FILE    = "backend/compose.yaml"

        BACKEND_TEST_PORT = "5001"
        BACKEND_PROD_PORT = "8080"
        FRONTEND_PROD_PORT = "80"
    }

    triggers {
        githubPush()
    }

    stages {

        // ============================================================
        // BACKEND TEST
        // ============================================================

        stage('Backend Test') {

            steps {

                echo "========================================="
                echo "===== BACKEND APPLICATION TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "Python version:"
                    python3 --version

                    echo "===== Compiling Backend Application ====="

                    cd backend

                    python3 -m py_compile app.py

                    echo "===== Backend Test PASSED ====="
                '''
            }
        }


        // ============================================================
        // BACKEND DOCKER BUILD
        // ============================================================

        stage('Backend Docker Build') {

            steps {

                echo "========================================="
                echo "===== BUILDING BACKEND IMAGE ====="
                echo "========================================="

                sh '''
                    set -e

                    docker build \
                        -t ${BACKEND_IMAGE}:test \
                        backend

                    echo "===== Backend Docker Build PASSED ====="
                '''
            }
        }


        // ============================================================
        // BACKEND CONTAINER TEST
        // ============================================================

        stage('Backend Container Test') {

            steps {

                echo "========================================="
                echo "===== BACKEND CONTAINER TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Removing Old Test Container ====="

                    docker rm -f devops-backend-test 2>/dev/null || true

                    echo "===== Checking Test Port ====="

                    if ss -lnt | grep -q ":${BACKEND_TEST_PORT} "; then
                        echo "ERROR: Port ${BACKEND_TEST_PORT} is already in use."
                        ss -lntp | grep ":${BACKEND_TEST_PORT} " || true
                        exit 1
                    fi

                    echo "Port ${BACKEND_TEST_PORT} is available."

                    echo "===== Starting Backend Test Container ====="

                    docker run -d \
                        --name devops-backend-test \
                        -p ${BACKEND_TEST_PORT}:5000 \
                        ${BACKEND_IMAGE}:test

                    echo "===== Waiting for Backend ====="

                    sleep 5

                    echo "===== Container Status ====="

                    docker ps \
                        --filter name=devops-backend-test \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'

                    echo "===== Testing Backend Health ====="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_TEST_PORT}/health

                    echo

                    echo "===== Testing Backend API ====="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_TEST_PORT}/api

                    echo

                    echo "===== Backend Container Test PASSED ====="
                '''
            }

            post {

                always {

                    echo "===== Cleaning Backend Test Container ====="

                    sh '''
                        docker rm -f devops-backend-test 2>/dev/null || true
                    '''
                }
            }
        }


        // ============================================================
        // BACKEND DOCKER PUSH
        // ============================================================

        stage('Backend Docker Push') {

            steps {

                echo "========================================="
                echo "===== PUSHING BACKEND IMAGE ====="
                echo "========================================="

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Docker Hub Login ====="

                        echo "$DOCKER_PASSWORD" | \
                            docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "===== Tagging Backend Image ====="

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


        // ============================================================
        // PREPARE DATABASE ENVIRONMENT
        // ============================================================

        stage('Prepare Database Environment') {

            steps {

                echo "========================================="
                echo "===== PREPARING DATABASE ENVIRONMENT ====="
                echo "========================================="

                withCredentials([
                    string(
                        credentialsId: 'postgres-password',
                        variable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Creating backend/.env ====="

                        cat > backend/.env <<EOF
POSTGRES_DB=employee_db
POSTGRES_USER=devops_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
EOF

                        chmod 600 backend/.env

                        echo "===== Environment File Created ====="

                        echo "POSTGRES_DB=employee_db"
                        echo "POSTGRES_USER=devops_user"
                        echo "POSTGRES_PASSWORD=********"

                        echo "===== Validating Docker Compose ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            config

                        echo "===== Compose Configuration VALID ====="
                    '''
                }
            }
        }


        // ============================================================
        // DEPLOY BACKEND + DATABASE
        // ============================================================

        stage('Deploy Backend and Database') {

            steps {

                echo "========================================="
                echo "===== DEPLOYING BACKEND + DATABASE ====="
                echo "========================================="

                withCredentials([
                    string(
                        credentialsId: 'postgres-password',
                        variable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Recreating Environment File ====="

                        cat > backend/.env <<EOF
POSTGRES_DB=employee_db
POSTGRES_USER=devops_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
EOF

                        chmod 600 backend/.env

                        echo "===== Stopping Existing Backend Deployment ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            down

                        echo "===== Removing Old Backend Test Container ====="

                        docker rm -f devops-backend-test 2>/dev/null || true

                        echo "===== Pulling Backend Images ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            pull

                        echo "===== Starting Backend + Database ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            up -d

                        echo "===== Backend Deployment Started ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            ps
                    '''
                }
            }
        }


        // ============================================================
        // BACKEND HEALTH CHECK
        // ============================================================

        stage('Backend Health Check') {

            steps {

                echo "========================================="
                echo "===== BACKEND PRODUCTION HEALTH ====="
                echo "========================================="

                withCredentials([
                    string(
                        credentialsId: 'postgres-password',
                        variable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        cat > backend/.env <<EOF
POSTGRES_DB=employee_db
POSTGRES_USER=devops_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
EOF

                        chmod 600 backend/.env

                        echo "===== Current Containers ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            ps

                        echo "===== Waiting for Backend Health ====="

                        HEALTH_OK=0

                        for i in 1 2 3 4 5 6 7 8 9 10
                        do

                            echo "Health check attempt $i/10"

                            if curl -fsS \
                                http://127.0.0.1:${BACKEND_PROD_PORT}/health
                            then

                                HEALTH_OK=1
                                break

                            fi

                            sleep 3

                        done

                        if [ "$HEALTH_OK" -ne 1 ]; then

                            echo "===== BACKEND HEALTH CHECK FAILED ====="

                            docker compose \
                                -p ${COMPOSE_PROJECT} \
                                --env-file backend/.env \
                                -f ${COMPOSE_FILE} \
                                logs --tail=100 backend

                            exit 1

                        fi

                        echo

                        echo "===== BACKEND HEALTH CHECK PASSED ====="

                        echo "===== API CHECK ====="

                        curl -fsS \
                            http://127.0.0.1:${BACKEND_PROD_PORT}/api

                        echo

                        echo "===== DATABASE STATUS ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            ps

                        echo "===== Backend Deployment VERIFIED ====="
                    '''
                }
            }
        }


        // ============================================================
        // FRONTEND TEST
        // ============================================================

        stage('Frontend Test') {

            steps {

                echo "========================================="
                echo "===== FRONTEND APPLICATION TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Checking Frontend Files ====="

                    test -f frontend/index.html
                    test -f frontend/style.css
                    test -f frontend/script.js
                    test -f frontend/Dockerfile

                    echo "index.html      : OK"
                    echo "style.css       : OK"
                    echo "script.js       : OK"
                    echo "Dockerfile      : OK"

                    echo "===== Frontend File Test PASSED ====="
                '''
            }
        }


        // ============================================================
        // FRONTEND DOCKER BUILD
        // ============================================================

        stage('Frontend Docker Build') {

            steps {

                echo "========================================="
                echo "===== BUILDING FRONTEND IMAGE ====="
                echo "========================================="

                sh '''
                    set -e

                    docker build \
                        -t ${FRONTEND_IMAGE}:test \
                        frontend

                    echo "===== Frontend Docker Build PASSED ====="
                '''
            }
        }


        // ============================================================
        // FRONTEND CONTAINER TEST
        // ============================================================

        stage('Frontend Container Test') {

            steps {

                echo "========================================="
                echo "===== FRONTEND CONTAINER TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Removing Old Frontend Test Container ====="

                    docker rm -f devops-frontend-ci-test 2>/dev/null || true

                    echo "===== Starting Frontend Test Container ====="

                    docker run -d \
                        --name devops-frontend-ci-test \
                        -p 8088:80 \
                        ${FRONTEND_IMAGE}:test

                    echo "===== Waiting for Nginx ====="

                    sleep 3

                    echo "===== Testing Frontend HTML ====="

                    curl -fsS \
                        http://127.0.0.1:8088/

                    echo

                    echo "===== Testing Frontend JavaScript ====="

                    curl -fsS \
                        http://127.0.0.1:8088/script.js

                    echo

                    echo "===== Testing Frontend CSS ====="

                    curl -fsS \
                        http://127.0.0.1:8088/style.css

                    echo

                    echo "===== Frontend Container Test PASSED ====="
                '''
            }

            post {

                always {

                    echo "===== Cleaning Frontend Test Container ====="

                    sh '''
                        docker rm -f devops-frontend-ci-test 2>/dev/null || true
                    '''
                }
            }
        }


        // ============================================================
        // FRONTEND DOCKER PUSH
        // ============================================================

        stage('Frontend Docker Push') {

            steps {

                echo "========================================="
                echo "===== PUSHING FRONTEND IMAGE ====="
                echo "========================================="

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Docker Hub Login ====="

                        echo "$DOCKER_PASSWORD" | \
                            docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "===== Tagging Frontend Image ====="

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


        // ============================================================
        // DEPLOY FRONTEND
        // ============================================================

        stage('Deploy Frontend') {

            steps {

                echo "========================================="
                echo "===== DEPLOYING FRONTEND ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Removing Existing Frontend Production Container ====="

                    docker rm -f devops-3tier-pipeline-frontend 2>/dev/null || true

                    echo "===== Removing Old Frontend Containers ====="

                    docker rm -f devops-frontend-prod 2>/dev/null || true
                    docker rm -f devops-frontend-ci-test 2>/dev/null || true

                    echo "===== Pulling Frontend Image ====="

                    docker pull \
                        ${FRONTEND_IMAGE}:latest

                    echo "===== Starting Frontend ====="

                    docker run -d \
                        --name devops-3tier-pipeline-frontend \
                        --restart unless-stopped \
                        -p ${FRONTEND_PROD_PORT}:80 \
                        ${FRONTEND_IMAGE}:latest

                    echo "===== Frontend Deployment Started ====="

                    docker ps \
                        --filter name=devops-3tier-pipeline-frontend \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'
                '''
            }
        }


        // ============================================================
        // FRONTEND HEALTH CHECK
        // ============================================================

        stage('Frontend Health Check') {

            steps {

                echo "========================================="
                echo "===== FRONTEND PRODUCTION HEALTH ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Waiting for Frontend ====="

                    FRONTEND_OK=0

                    for i in 1 2 3 4 5 6 7 8 9 10
                    do

                        echo "Frontend health check attempt $i/10"

                        if curl -fsS \
                            http://127.0.0.1:${FRONTEND_PROD_PORT}/
                        then

                            FRONTEND_OK=1
                            break

                        fi

                        sleep 2

                    done

                    if [ "$FRONTEND_OK" -ne 1 ]; then

                        echo "===== FRONTEND HEALTH CHECK FAILED ====="

                        docker logs \
                            --tail=100 \
                            devops-3tier-pipeline-frontend

                        exit 1

                    fi

                    echo

                    echo "===== FRONTEND HEALTH CHECK PASSED ====="

                    echo "===== Frontend Container ====="

                    docker ps \
                        --filter name=devops-3tier-pipeline-frontend \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'
                '''
            }
        }


        // ============================================================
        // FINAL SYSTEM VERIFICATION
        // ============================================================

        stage('Final System Verification') {

            steps {

                echo "========================================="
                echo "===== FINAL SYSTEM VERIFICATION ====="
                echo "========================================="

                sh '''
                    set -e

                    echo
                    echo "========================================="
                    echo "===== BACKEND HEALTH ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/health

                    echo

                    echo
                    echo "========================================="
                    echo "===== BACKEND API ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/api

                    echo

                    echo
                    echo "========================================="
                    echo "===== FRONTEND ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${FRONTEND_PROD_PORT}/ \
                        -o /tmp/frontend.html

                    grep -q \
                        'DevOps Employee Portal' \
                        /tmp/frontend.html

                    echo "Frontend HTML verified successfully."

                    echo

                    echo "========================================="
                    echo "===== RUNNING CONTAINERS ====="
                    echo "========================================="

                    docker ps \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'

                    echo

                    echo "========================================="
                    echo "===== SYSTEM VERIFICATION PASSED ====="
                    echo "========================================="
                '''
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        always {

            echo "========================================="
            echo "===== CLEANING PIPELINE ENVIRONMENT ====="
            echo "========================================="

            sh '''
                rm -f backend/.env

                docker rm -f devops-backend-test 2>/dev/null || true
                docker rm -f devops-frontend-ci-test 2>/dev/null || true
            '''
        }

        success {

            echo "========================================="
            echo "===== PIPELINE EXECUTION COMPLETED ====="
            echo "========================================="

            echo "===== APPLICATION DEPLOYED SUCCESSFULLY ====="

            echo "Backend  : http://SERVER-IP:8080"
            echo "Frontend : http://SERVER-IP"
        }

        failure {

            echo "========================================="
            echo "===== PIPELINE FAILED ====="
            echo "========================================="

            echo "Check the failed stage above."
        }
    }
}
