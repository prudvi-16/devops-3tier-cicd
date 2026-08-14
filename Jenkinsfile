pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'prudvik2026/devops-backend'
        COMPOSE_FILE = 'backend/compose.yaml'
        COMPOSE_PROJECT = 'devops-3tier-pipeline'
    }

    stages {

        // =========================================================
        // 1. APPLICATION TEST
        // =========================================================
        stage('Test') {
            steps {
                echo '========================================='
                echo '===== Running Application Test ====='
                echo '========================================='

                sh '''
                    set -e

                    python3 --version

                    echo "===== Compiling Backend Application ====="

                    cd backend

                    python3 -m py_compile app.py

                    echo "===== Application Test PASSED ====="
                '''
            }
        }


        // =========================================================
        // 2. DOCKER BUILD
        // =========================================================
        stage('Docker Build') {
            steps {
                echo '========================================='
                echo '===== Building Backend Docker Image ====='
                echo '========================================='

                sh '''
                    set -e

                    docker build \
                        -t ${DOCKER_IMAGE}:test \
                        backend

                    echo "===== Docker Build PASSED ====="
                '''
            }
        }


        // =========================================================
        // 3. CONTAINER TEST
        // =========================================================
        stage('Container Test') {
            steps {
                echo '========================================='
                echo '===== Starting Test Container ====='
                echo '========================================='

                sh '''
                    set -e

                    docker rm -f devops-backend-test 2>/dev/null || true

                    docker run -d \
                        --name devops-backend-test \
                        -p 5000:5000 \
                        ${DOCKER_IMAGE}:test

                    echo "===== Waiting for Backend ====="

                    sleep 5

                    echo "===== Testing Health Endpoint ====="

                    curl -fsS http://127.0.0.1:5000/health

                    echo ""
                    echo "===== Container Test PASSED ====="
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


        // =========================================================
        // 4. DOCKER HUB PUSH
        // =========================================================
        stage('Docker Push') {
            steps {
                echo '========================================='
                echo '===== Pushing Docker Image ====='
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

                        echo "===== Tagging Build Image ====="

                        docker tag \
                            ${DOCKER_IMAGE}:test \
                            ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        docker tag \
                            ${DOCKER_IMAGE}:test \
                            ${DOCKER_IMAGE}:latest

                        echo "===== Pushing Build ${BUILD_NUMBER} ====="

                        docker push \
                            ${DOCKER_IMAGE}:${BUILD_NUMBER}

                        echo "===== Pushing Latest ====="

                        docker push \
                            ${DOCKER_IMAGE}:latest

                        docker logout

                        echo "===== Docker Push PASSED ====="
                    '''
                }
            }
        }


        // =========================================================
        // 5. PREPARE DATABASE ENVIRONMENT
        // =========================================================
        stage('Prepare Environment') {
            steps {
                echo '========================================='
                echo '===== Preparing Deployment Environment ====='
                echo '========================================='

                /*
                 * backend/.env is intentionally NOT stored in Git.
                 *
                 * Jenkins creates it temporarily from Jenkins credentials.
                 *
                 * REQUIRED JENKINS CREDENTIAL:
                 *
                 * ID: db-credentials
                 * TYPE: Username with password
                 *
                 * Username = devops_user
                 * Password = your PostgreSQL password
                 */

                withCredentials([
                    usernamePassword(
                        credentialsId: 'db-credentials',
                        usernameVariable: 'POSTGRES_USER_SECRET',
                        passwordVariable: 'POSTGRES_PASSWORD_SECRET'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "===== Creating temporary backend/.env ====="

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

                        echo "===== Validating Compose Configuration ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            config > /tmp/devops-compose-config.yml

                        echo "===== Compose Configuration VALID ====="
                    '''
                }
            }
        }


        // =========================================================
        // 6. DEPLOY BACKEND + DATABASE
        // =========================================================
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
 B                   )
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

                        echo "===== Stopping Existing Deployment ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            down

                        echo "===== Removing Old Backend Test Containers ====="

                        docker rm -f devops-backend-test 2>/dev/null || true

                        echo "===== Pulling Docker Hub Images ====="

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

                        echo "===== Deployment Started ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            ps
                    '''
                }
            }
        }


        // =========================================================
        // 7. DEPLOYMENT HEALTH CHECK
        // =========================================================
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
                            -f ${COMPOSE_FILE} \
                            ps

                        echo "===== Waiting for Backend Health ====="

                        for i in 1 2 3 4 5 6 7 8 9 10
                        do

                            echo "Health check attempt $i/10"

                            if curl -fsS http://127.0.0.1:8080/health
                            then
                                echo ""
                                echo "========================================="
                                echo "===== BACKEND HEALTH CHECK PASSED ====="
                                echo "========================================="

                                echo "===== API CHECK ====="

                                curl -fsS http://127.0.0.1:8080/api

                                echo ""

                                echo "===== Database Health ====="

                                docker compose \
                                    -p ${COMPOSE_PROJECT} \
                                    --env-file backend/.env \
                                    -f ${COMPOSE_FILE} \
                                    ps

                                exit 0
                            fi

                            echo "Backend is not ready yet..."

                            sleep 5
                        done

                        echo ""
                        echo "========================================="
                        echo "===== BACKEND HEALTH CHECK FAILED ====="
                        echo "========================================="

                        echo "===== Compose Status ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            ps

                        echo "===== Backend Logs ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            logs --tail=100 backend

                        echo "===== Database Logs ====="

                        docker compose \
                            -p ${COMPOSE_PROJECT} \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            logs --tail=100 db

                        exit 1
                    '''
                }
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================
    post {

        success {
            echo '''
=========================================
===== PIPELINE SUCCESS =====
=========================================
'''

            echo "Docker Image: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
            echo "Docker Image: ${DOCKER_IMAGE}:latest"

            echo '''
=========================================
===== APPLICATION DEPLOYED =====
=========================================
'''
        }

        failure {
            echo '''
=========================================
===== PIPELINE FAILED =====
=========================================
'''

            echo 'Check the failed stage and container logs.'
        }

        always {
            echo '===== Pipeline Execution Completed ====='

            /*
             * Remove temporary environment file.
             * It is NOT committed to Git.
             */
            sh '''
                rm -f backend/.env 2>/dev/null || true
            '''
        }
    }
}
