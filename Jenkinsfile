pipeline {

    agent any

    environment {
        BACKEND_IMAGE = 'prudvik2026/devops-backend'
        FRONTEND_IMAGE = 'prudvik2026/devops-frontend'
        COMPOSE_PROJECT = 'devops-3tier-pipeline'
    }

    stages {

        /*
         * ============================================================
         * STAGE 1 - BACKEND APPLICATION TEST
         * ============================================================
         */

        stage('Backend Test') {

            steps {

                echo '========================================='
                echo '===== BACKEND APPLICATION TEST ====='
                echo '========================================='

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


        /*
         * ============================================================
         * STAGE 2 - BACKEND DOCKER BUILD
         * ============================================================
         */

        stage('Backend Docker Build') {

            steps {

                echo '========================================='
                echo '===== BUILDING BACKEND IMAGE ====='
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


        /*
         * ============================================================
         * STAGE 3 - BACKEND CONTAINER TEST
         * ============================================================
         */

        stage('Backend Container Test') {

            steps {

                echo '========================================='
                echo '===== BACKEND CONTAINER TEST ====='
                echo '========================================='

                sh '''
                    set -e

                    echo "===== Removing Old Test Container ====="

                    docker rm -f devops-backend-test 2>/dev/null || true

                    echo "===== Starting Backend Test Container ====="

                    docker run -d \
                        --name devops-backend-test \
                        -p 5000:5000 \
                        ${BACKEND_IMAGE}:test

                    echo "===== Waiting for Backend ====="

                    sleep 5

                    echo "===== Testing Backend Health ====="

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


        /*
         * ============================================================
         * STAGE 4 - BACKEND DOCKER HUB PUSH
         * ============================================================
         */

        stage('Backend Docker Push') {

            steps {

                echo '========================================='
                echo '===== PUSHING BACKEND IMAGE ====='
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

                        echo "===== Docker Hub Login ====="

                        echo "$DOCKER_PASSWORD" | docker login \
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


        /*
         * ============================================================
         * STAGE 5 - PREPARE DATABASE ENVIRONMENT
         * ============================================================
         */

        stage('Prepare Database Environment') {

            steps {

                echo '========================================='
                echo '===== PREPARING DATABASE ENVIRONMENT ====='
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

                        echo "===== Creating backend/.env ====="

                        cat > backend/.env <<EOF
POSTGRES_DB=employee_db
POSTGRES_USER=${POSTGRES_USER_SECRET}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
EOF

                        chmod 600 backend/.env

                        echo "===== Environment File Created ====="

                        echo "POSTGRES_DB=employee_db"
                        echo "POSTGRES_USER=${POSTGRES_USER_SECRET}"
                        echo "POSTGRES_PASSWORD=********"

                        echo "===== Validating Docker Compose ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            config

                        echo "===== Compose Configuration VALID ====="
                    '''
                }
            }
        }


        /*
         * ============================================================
         * STAGE 6 - BACKEND + DATABASE DEPLOYMENT
         * ============================================================
         */

        stage('Deploy Backend and Database') {

            steps {

                echo '========================================='
                echo '===== DEPLOYING BACKEND + DATABASE ====='
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

                        cat > backend/.env <<EOF
POSTGRES_DB=employee_db
POSTGRES_USER=${POSTGRES_USER_SECRET}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
EOF

                        chmod 600 backend/.env

                        echo "===== Stopping Existing Backend Deployment ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            down

                        echo "===== Removing Old Backend Test Containers ====="

                        docker rm -f devops-backend-test 2>/dev/null || true

                        echo "===== Pulling Backend Images ====="

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

                        echo "===== Backend Deployment Started ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            ps
                    '''
                }
            }
        }


        /*
         * ============================================================
         * STAGE 7 - BACKEND DEPLOYMENT HEALTH CHECK
         * ============================================================
         */

        stage('Backend Health Check') {

            steps {

                echo '========================================='
                echo '===== BACKEND PRODUCTION HEALTH ====='
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

                        cat > backend/.env <<EOF
POSTGRES_DB=employee_db
POSTGRES_USER=${POSTGRES_USER_SECRET}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_SECRET}
EOF

                        chmod 600 backend/.env

                        echo "===== Current Containers ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            ps

                        echo "===== Waiting for Backend Health ====="

                        for i in 1 2 3 4 5 6 7 8 9 10
                        do

                            echo "Health check attempt $i/10"

                            if curl -fsS \
                                http://127.0.0.1:8080/health
                            then

                                echo ""
                                echo "========================================="
                                echo "===== BACKEND HEALTH CHECK PASSED ====="
                                echo "========================================="

                                break

                            fi

                            echo "Backend is not ready yet..."

                            sleep 5

                            if [ "$i" = "10" ]
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

                        done

                        echo "===== API CHECK ====="

                        curl -fsS \
                            http://127.0.0.1:8080/api

                        echo ""

                        echo "===== DATABASE STATUS ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f backend/compose.yaml \
                            ps

                        echo "===== Backend Deployment VERIFIED ====="
                    '''
                }
            }
        }


        /*
         * ============================================================
         * STAGE 8 - FRONTEND APPLICATION TEST
         * ============================================================
         */

        stage('Frontend Test') {

            steps {

                echo '========================================='
                echo '===== FRONTEND APPLICATION TEST ====='
                echo '========================================='

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


        /*
         * ============================================================
         * STAGE 9 - FRONTEND DOCKER BUILD
         * ============================================================
         */

        stage('Frontend Docker Build') {

            steps {

                echo '========================================='
                echo '===== BUILDING FRONTEND IMAGE ====='
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


        /*
         * ============================================================
         * STAGE 10 - FRONTEND CONTAINER TEST
         * ============================================================
         */

        stage('Frontend Container Test') {

            steps {

                echo '========================================='
                echo '===== FRONTEND CONTAINER TEST ====='
                echo '========================================='

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

                    echo ""

                    echo "===== Testing Frontend JavaScript ====="

                    curl -fsS \
                        http://127.0.0.1:8088/script.js

                    echo ""

                    echo "===== Testing Frontend CSS ====="

                    curl -fsS \
                        http://127.0.0.1:8088/style.css

                    echo ""

                    echo "===== Frontend Container Test PASSED ====="
                '''
            }

            post {

                always {

                    echo '===== Cleaning Frontend Test Container ====='

                    sh '''
                        docker rm -f devops-frontend-ci-test 2>/dev/null || true
                    '''
                }
            }
        }


        /*
         * ============================================================
         * STAGE 11 - FRONTEND DOCKER HUB PUSH
         * ============================================================
         */

        stage('Frontend Docker Push') {

            steps {

                echo '========================================='
                echo '===== PUSHING FRONTEND IMAGE ====='
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

                        echo "===== Docker Hub Login ====="

                        echo "$DOCKER_PASSWORD" | docker login \
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


        /*
         * ============================================================
         * STAGE 12 - FRONTEND PRODUCTION DEPLOYMENT
         * ============================================================
         */

        stage('Deploy Frontend') {

            steps {

                echo '========================================='
                echo '===== DEPLOYING FRONTEND ====='
                echo '========================================='

                sh '''
                    set -e

                    echo "===== Removing Existing Frontend Container ====="

                    docker rm -f devops-frontend-prod 2>/dev/null || true

                    echo "===== Removing Old Frontend Test Container ====="

                    docker rm -f devops-frontend-ci-test 2>/dev/null || true

                    echo "===== Pulling Frontend Image ====="

                    docker pull ${FRONTEND_IMAGE}:latest

                    echo "===== Starting Frontend ====="

                    docker run -d \
                        --name devops-frontend-prod \
                        --restart unless-stopped \
                        -p 80:80 \
                        ${FRONTEND_IMAGE}:latest

                    echo "===== Frontend Deployment Started ====="

                    docker ps \
                        --filter name=devops-frontend-prod \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'
                '''
            }
        }


        /*
         * ============================================================
         * STAGE 13 - FRONTEND PRODUCTION HEALTH CHECK
         * ============================================================
         */

        stage('Frontend Health Check') {

            steps {

                echo '========================================='
                echo '===== FRONTEND PRODUCTION HEALTH ====='
                echo '========================================='

                sh '''
                    set -e

                    echo "===== Waiting for Frontend ====="

                    for i in 1 2 3 4 5
                    do

                        echo "Frontend health check attempt $i/5"

                        if curl -fsS \
                            http://127.0.0.1/
                        then

                            echo ""

                            echo "========================================="
                            echo "===== FRONTEND HEALTH CHECK PASSED ====="
                            echo "========================================="

                            break

                        fi

                        echo "Frontend is not ready yet..."

                        sleep 3

                        if [ "$i" = "5" ]
                        then

                            echo "===== FRONTEND HEALTH CHECK FAILED ====="

                            docker ps \
                                --filter name=devops-frontend-prod

                            docker logs \
                                --tail=50 \
                                devops-frontend-prod

                            exit 1
                        fi

                    done

                    echo "===== Testing Frontend JavaScript ====="

                    curl -fsS \
                        http://127.0.0.1/script.js \
                        > /dev/null

                    echo "Frontend JavaScript: OK"

                    echo "===== Testing Frontend CSS ====="

                    curl -fsS \
                        http://127.0.0.1/style.css \
                        > /dev/null

                    echo "Frontend CSS: OK"

                    echo "===== Frontend Deployment VERIFIED ====="
                '''
            }
        }


        /*
         * ============================================================
         * STAGE 14 - FINAL SYSTEM VERIFICATION
         * ============================================================
         */

        stage('Final System Verification') {

            steps {

                echo '========================================='
                echo '===== FINAL 3-TIER VERIFICATION ====='
                echo '========================================='

                sh '''
                    set -e

                    echo ""
                    echo "========== FRONTEND =========="

                    docker ps \
                        --filter name=devops-frontend-prod \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'

                    echo ""
                    echo "========== BACKEND + DATABASE =========="

                    docker ps \
                        --filter name=${COMPOSE_PROJECT} \
                        --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'

                    echo ""
                    echo "========== FRONTEND TEST =========="

                    curl -fsS \
                        http://127.0.0.1/ \
                        > /dev/null

                    echo "Frontend: UP"

                    echo ""
                    echo "========== BACKEND TEST =========="

                    curl -fsS \
                        http://127.0.0.1:8080/health

                    echo ""

                    echo ""
                    echo "========== API TEST =========="

                    curl -fsS \
                        http://127.0.0.1:8080/api

                    echo ""

                    echo ""
                    echo "========================================="
                    echo "===== COMPLETE 3-TIER SYSTEM: UP ====="
                    echo "========================================="
                '''
            }
        }
    }


    /*
     * ================================================================
     * POST ACTIONS
     * ================================================================
     */

    post {

        success {

            echo '========================================='
            echo '===== PIPELINE SUCCESS ====='
            echo '========================================='

            echo "Backend Image:"
            echo "${BACKEND_IMAGE}:${BUILD_NUMBER}"

            echo "Backend Latest:"
            echo "${BACKEND_IMAGE}:latest"

            echo "Frontend Image:"
            echo "${FRONTEND_IMAGE}:${BUILD_NUMBER}"

            echo "Frontend Latest:"
            echo "${FRONTEND_IMAGE}:latest"

            echo '========================================='
            echo '===== APPLICATION DEPLOYED ====='
            echo '========================================='
        }


        failure {

            echo '========================================='
            echo '===== PIPELINE FAILED ====='
            echo '========================================='

            echo 'Check the failed stage above.'
        }


        always {

            echo '========================================='
            echo '===== CLEANING PIPELINE ENVIRONMENT ====='
            echo '========================================='

            sh '''
                rm -f backend/.env 2>/dev/null || true

                docker rm -f devops-backend-test 2>/dev/null || true

                docker rm -f devops-frontend-ci-test 2>/dev/null || true
            '''

            echo '===== Pipeline Execution Completed ====='
        }
    }
}
