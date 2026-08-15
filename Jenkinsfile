pipeline {

    agent any
   
    triggers {
        githubPush()
    }

    environment {

        // ============================================================
        // DOCKER HUB
        // ============================================================

        DOCKER_USER = "prudvik2026"

        BACKEND_IMAGE = "prudvik2026/devops-backend"
        FRONTEND_IMAGE = "prudvik2026/devops-frontend"


        // ============================================================
        // PRODUCTION PORTS
        // ============================================================

        BACKEND_PROD_PORT = "8080"
        FRONTEND_PROD_PORT = "80"


        // ============================================================
        // COMPOSE
        // ============================================================

        COMPOSE_FILE = "backend/compose.yaml"


        // ============================================================
        // DATABASE
        // ============================================================

        POSTGRES_DB = "employee_db"
        POSTGRES_USER = "devops_user"
        POSTGRES_PASSWORD = "devops_password"
    }


    stages {


        // ============================================================
        // 1. BACKEND APPLICATION TEST
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

                    echo "===== Backend Application Test PASSED ====="
                '''
            }
        }


        // ============================================================
        // 2. BACKEND DOCKER BUILD
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
        // 3. BACKEND CONTAINER TEST
        //
        // IMPORTANT:
        // NO HOST PORT IS USED.
        //
        // A temporary PostgreSQL container is created on a
        // temporary Docker network.
        // ============================================================

        stage('Backend Container Test') {

            steps {

                echo "========================================="
                echo "===== BACKEND CONTAINER TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    TEST_NETWORK="devops-backend-ci-network"
                    TEST_DB="devops-backend-ci-db"
                    TEST_CONTAINER="devops-backend-test"


                    echo "===== Cleaning Previous CI Resources ====="

                    docker rm -f ${TEST_CONTAINER} 2>/dev/null || true
                    docker rm -f ${TEST_DB} 2>/dev/null || true
                    docker network rm ${TEST_NETWORK} 2>/dev/null || true


                    echo "===== Creating Temporary CI Network ====="

                    docker network create ${TEST_NETWORK}


                    echo "===== Starting Temporary PostgreSQL ====="

                    docker run -d \
                        --name ${TEST_DB} \
                        --network ${TEST_NETWORK} \
                        -e POSTGRES_DB=${POSTGRES_DB} \
                        -e POSTGRES_USER=${POSTGRES_USER} \
                        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
                        postgres:16-alpine


                    echo "===== Waiting for PostgreSQL ====="

                    DB_READY=false

                    for i in $(seq 1 30); do

                        if docker exec ${TEST_DB} \
                            pg_isready \
                            -U ${POSTGRES_USER} \
                            -d ${POSTGRES_DB} >/dev/null 2>&1
                        then
                            DB_READY=true
                            echo "PostgreSQL is ready."
                            break
                        fi

                        echo "Waiting for PostgreSQL... attempt ${i}/30"

                        sleep 2

                    done


                    if [ "${DB_READY}" != "true" ]; then

                        echo "ERROR: PostgreSQL did not become ready."

                        docker logs ${TEST_DB} || true

                        exit 1
                    fi


                    echo "===== Starting Backend CI Container ====="

                    docker run -d \
                        --name ${TEST_CONTAINER} \
                        --network ${TEST_NETWORK} \
                        -e DB_HOST=${TEST_DB} \
                        -e DB_PORT=5432 \
                        -e DB_NAME=${POSTGRES_DB} \
                        -e DB_USER=${POSTGRES_USER} \
                        -e DB_PASSWORD=${POSTGRES_PASSWORD} \
                        ${BACKEND_IMAGE}:test


                    echo "===== Waiting for Backend ====="

                    sleep 5


                    echo "===== Backend Container Status ====="

                    docker ps \
                        --filter "name=${TEST_CONTAINER}" \
                        --format "table {{.Names}}\\t{{.Status}}"


                    echo "===== Backend Container Logs ====="

                    docker logs ${TEST_CONTAINER}


                    echo "===== Checking Backend Container ====="

                    if ! docker ps \
                        --format '{{.Names}}' \
                        | grep -qx "${TEST_CONTAINER}"
                    then

                        echo "ERROR: Backend container is not running."

                        docker logs ${TEST_CONTAINER} || true

                        exit 1
                    fi


                    echo "===== Checking psycopg2 ====="

                    docker exec ${TEST_CONTAINER} \
                        python3 -c "import psycopg2; print('psycopg2 OK')"


                    echo "===== Checking Backend Health ====="

                    docker exec ${TEST_CONTAINER} \
                        python3 -c '
import urllib.request
import sys

url = "http://127.0.0.1:5000/health"

try:
    response = urllib.request.urlopen(url, timeout=5)
    body = response.read().decode()

    print("HTTP Status:", response.status)
    print("Response:", body)

    if response.status != 200:
        sys.exit(1)

except Exception as e:
    print("Health check failed:", e)
    sys.exit(1)
'


                    echo "===== Checking Backend API ====="

                    docker exec ${TEST_CONTAINER} \
                        python3 -c '
import urllib.request
import sys

url = "http://127.0.0.1:5000/api"

try:
    response = urllib.request.urlopen(url, timeout=5)
    body = response.read().decode()

    print("HTTP Status:", response.status)
    print("Response:", body)

    if response.status != 200:
        sys.exit(1)

except Exception as e:
    print("API check failed:", e)
    sys.exit(1)
'


                    echo "===== Testing CREATE Employee ====="

                    docker exec ${TEST_CONTAINER} \
                        python3 -c '
import urllib.request
import json
import sys

url = "http://127.0.0.1:5000/employees"

data = {
    "name": "Jenkins Test User",
    "email": "jenkins-test@example.com",
    "department": "DevOps"
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:

    response = urllib.request.urlopen(request, timeout=5)

    body = response.read().decode()

    print("HTTP Status:", response.status)
    print("Response:", body)

    if response.status != 201:
        sys.exit(1)

except Exception as e:

    print("CREATE employee failed:", e)
    sys.exit(1)
'


                    echo "===== Testing GET Employees ====="

                    docker exec ${TEST_CONTAINER} \
                        python3 -c '
import urllib.request
import sys

url = "http://127.0.0.1:5000/employees"

try:

    response = urllib.request.urlopen(url, timeout=5)

    body = response.read().decode()

    print("HTTP Status:", response.status)
    print("Response:", body)

    if response.status != 200:
        sys.exit(1)

except Exception as e:

    print("GET employees failed:", e)
    sys.exit(1)
'


                    echo "===== Backend Container Test PASSED ====="


                    echo "===== Removing Backend CI Container ====="

                    docker rm -f ${TEST_CONTAINER} 2>/dev/null || true


                    echo "===== Removing PostgreSQL CI Container ====="

                    docker rm -f ${TEST_DB} 2>/dev/null || true


                    echo "===== Removing CI Network ====="

                    docker network rm ${TEST_NETWORK} 2>/dev/null || true
                '''
            }

            post {

                always {

                    sh '''
                        docker rm -f devops-backend-test 2>/dev/null || true
                        docker rm -f devops-backend-ci-db 2>/dev/null || true
                        docker network rm devops-backend-ci-network 2>/dev/null || true
                    '''
                }
            }
        }


        // ============================================================
        // 4. BACKEND DOCKER PUSH
        // ============================================================

        stage('Backend Docker Push') {

            steps {

                echo "========================================="
                echo "===== PUSHING BACKEND IMAGE ====="
                echo "========================================="

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "${DOCKER_PASSWORD}" | docker login \
                            -u "${DOCKER_USERNAME}" \
                            --password-stdin

                        docker tag \
                            ${BACKEND_IMAGE}:test \
                            ${BACKEND_IMAGE}:latest

                        docker push \
                            ${BACKEND_IMAGE}:test

                        docker push \
                            ${BACKEND_IMAGE}:latest

                        docker logout

                        echo "===== Backend Docker Push PASSED ====="
                    '''
                }
            }
        }


        // ============================================================
        // 5. PREPARE DATABASE ENVIRONMENT
        // ============================================================

        stage('Prepare Database Environment') {

            steps {

                echo "========================================="
                echo "===== PREPARING DATABASE ENVIRONMENT ====="
                echo "========================================="

                sh '''
                    set -e

                    cat > backend/.env <<EOF
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF

                    echo "===== Database Environment Prepared ====="

                    cat backend/.env | sed 's/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=********/'
                '''
            }
        }


        // ============================================================
        // 6. DEPLOY BACKEND + DATABASE
        // ============================================================

        stage('Deploy Backend and Database') {

            steps {

                echo "========================================="
                echo "===== DEPLOYING BACKEND + DATABASE ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Stopping Existing Backend Stack ====="

                    docker compose \
                        --env-file backend/.env \
                        -f ${COMPOSE_FILE} \
                        down || true


                    echo "===== Pulling Latest Images ====="

                    docker pull ${BACKEND_IMAGE}:latest

                    docker pull postgres:16-alpine


                    echo "===== Starting Backend + PostgreSQL ====="

                    docker compose \
                        --env-file backend/.env \
                        -f ${COMPOSE_FILE} \
                        up -d


                    echo "===== Waiting for Services ====="

                    sleep 10


                    echo "===== Compose Status ====="

                    docker compose \
                        --env-file backend/.env \
                        -f ${COMPOSE_FILE} \
                        ps


                    echo "===== Backend + Database Deployment Completed ====="
                '''
            }
        }


        // ============================================================
        // 7. BACKEND HEALTH CHECK
        // ============================================================

        stage('Backend Health Check') {

            steps {

                echo "========================================="
                echo "===== BACKEND HEALTH CHECK ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Waiting for Backend Health ====="

                    BACKEND_READY=false

                    for i in $(seq 1 15); do

                        echo "Backend health check attempt ${i}/15"

                        if curl -fsS \
                            http://127.0.0.1:${BACKEND_PROD_PORT}/health
                        then

                            echo ""
                            echo "Backend health check PASSED."

                            BACKEND_READY=true

                            break
                        fi

                        sleep 3
                    done


                    if [ "${BACKEND_READY}" != "true" ]; then

                        echo "ERROR: Backend health check failed."

                        docker compose \
                            --env-file backend/.env \
                            -f ${COMPOSE_FILE} \
                            logs backend || true

                        exit 1
                    fi


                    echo "===== Backend API Check ====="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/api

                    echo ""

                    echo "===== Backend Employee API Check ====="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/employees

                    echo ""

                    echo "===== Backend Health/API Checks PASSED ====="
                '''
            }
        }


        // ============================================================
        // 8. FRONTEND APPLICATION TEST
        // ============================================================

        stage('Frontend Test') {

            steps {

                echo "========================================="
                echo "===== FRONTEND APPLICATION TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    test -f frontend/index.html
                    test -f frontend/script.js

                    echo "Frontend files found."

                    echo "===== Frontend Application Test PASSED ====="
                '''
            }
        }


        // ============================================================
        // 9. FRONTEND DOCKER BUILD
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
        // 10. FRONTEND CONTAINER TEST
        //
        // NO HOST PORT USED.
        // ============================================================

        stage('Frontend Container Test') {

            steps {

                echo "========================================="
                echo "===== FRONTEND CONTAINER TEST ====="
                echo "========================================="

                sh '''
                    set -e

                    FRONTEND_TEST_CONTAINER="devops-frontend-ci-test"


                    echo "===== Removing Old Frontend Test Container ====="

                    docker rm -f ${FRONTEND_TEST_CONTAINER} 2>/dev/null || true


                    echo "===== Starting Frontend Test Container ====="

                    docker run -d \
                        --name ${FRONTEND_TEST_CONTAINER} \
                        ${FRONTEND_IMAGE}:test


                    echo "===== Waiting for Frontend ====="

                    sleep 5


                    echo "===== Frontend Container Status ====="

                    docker ps \
                        --filter "name=${FRONTEND_TEST_CONTAINER}" \
                        --format "table {{.Names}}\\t{{.Status}}"


                    echo "===== Checking Frontend Container ====="

                    if ! docker ps \
                        --format '{{.Names}}' \
                        | grep -qx "${FRONTEND_TEST_CONTAINER}"
                    then

                        echo "ERROR: Frontend container is not running."

                        docker logs ${FRONTEND_TEST_CONTAINER} || true

                        exit 1
                    fi


                    echo "===== Testing Nginx Configuration ====="

                    docker exec ${FRONTEND_TEST_CONTAINER} nginx -t


                    echo "===== Testing Frontend HTTP ====="

                    docker exec ${FRONTEND_TEST_CONTAINER} \
                        wget -qO- http://127.0.0.1:80/ \
                        > /tmp/frontend-test.html


                    echo "===== Frontend Response ====="

                    head -20 /tmp/frontend-test.html


                    echo "===== Frontend Container Test PASSED ====="

                    docker rm -f ${FRONTEND_TEST_CONTAINER} 2>/dev/null || true
                '''
            }

            post {

                always {

                    sh '''
                        docker rm -f devops-frontend-ci-test 2>/dev/null || true
                    '''
                }
            }
        }


        // ============================================================
        // 11. FRONTEND DOCKER PUSH
        // ============================================================

        stage('Frontend Docker Push') {

            steps {

                echo "========================================="
                echo "===== PUSHING FRONTEND IMAGE ====="
                echo "========================================="

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "${DOCKER_PASSWORD}" | docker login \
                            -u "${DOCKER_USERNAME}" \
                            --password-stdin

                        docker tag \
                            ${FRONTEND_IMAGE}:test \
                            ${FRONTEND_IMAGE}:latest

                        docker push \
                            ${FRONTEND_IMAGE}:test

                        docker push \
                            ${FRONTEND_IMAGE}:latest

                        docker logout

                        echo "===== Frontend Docker Push PASSED ====="
                    '''
                }
            }
        }


        // ============================================================
        // 12. DEPLOY FRONTEND
        // ============================================================

        stage('Deploy Frontend') {

            steps {

                echo "========================================="
                echo "===== DEPLOYING FRONTEND ====="
                echo "========================================="

                sh '''
                    set -e

                    echo "===== Removing Existing Frontend ====="

                    docker rm -f devops-3tier-pipeline-frontend 2>/dev/null || true


                    echo "===== Pulling Latest Frontend Image ====="

                    docker pull ${FRONTEND_IMAGE}:latest


                    echo "===== Starting Frontend ====="

                    docker run -d \
                        --name devops-3tier-pipeline-frontend \
                        -p ${FRONTEND_PROD_PORT}:80 \
                        ${FRONTEND_IMAGE}:latest


                    echo "===== Frontend Deployment Completed ====="

                    docker ps \
                        --filter "name=devops-3tier-pipeline-frontend" \
                        --format "table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}"
                '''
            }
        }


        // ============================================================
        // 13. FRONTEND HEALTH CHECK
        // ============================================================

        stage('Frontend Health Check') {

            steps {

                echo "========================================="
                echo "===== FRONTEND HEALTH CHECK ====="
                echo "========================================="

                sh '''
                    set -e

                    FRONTEND_READY=false


                    for i in $(seq 1 10); do

                        echo "Frontend health check attempt ${i}/10"

                        if curl -fsS \
                            http://127.0.0.1:${FRONTEND_PROD_PORT}/ \
                            >/dev/null
                        then

                            echo "Frontend health check PASSED."

                            FRONTEND_READY=true

                            break
                        fi

                        sleep 2
                    done


                    if [ "${FRONTEND_READY}" != "true" ]; then

                        echo "ERROR: Frontend health check failed."

                        docker logs \
                            devops-3tier-pipeline-frontend || true

                        exit 1
                    fi


                    echo "===== Frontend Health Check PASSED ====="
                '''
            }
        }


        // ============================================================
        // 14. FINAL SYSTEM VERIFICATION
        // ============================================================

        stage('Final System Verification') {

            steps {

                echo "========================================="
                echo "===== FINAL SYSTEM VERIFICATION ====="
                echo "========================================="

                sh '''
                    set -e


                    echo "========================================="
                    echo "===== BACKEND HEALTH ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/health

                    echo ""


                    echo "========================================="
                    echo "===== BACKEND API ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/api

                    echo ""


                    echo "========================================="
                    echo "===== EMPLOYEE API ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${BACKEND_PROD_PORT}/employees

                    echo ""


                    echo "========================================="
                    echo "===== FRONTEND ====="
                    echo "========================================="

                    curl -fsS \
                        http://127.0.0.1:${FRONTEND_PROD_PORT}/ \
                        >/dev/null

                    echo "Frontend HTTP response: OK"


                    echo "========================================="
                    echo "===== DOCKER CONTAINERS ====="
                    echo "========================================="

                    docker ps \
                        --format "table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}"


                    echo "========================================="
                    echo "===== COMPOSE STATUS ====="
                    echo "========================================="

                    docker compose \
                        --env-file backend/.env \
                        -f ${COMPOSE_FILE} \
                        ps


                    echo "========================================="
                    echo "===== APPLICATION DEPLOYED SUCCESSFULLY ====="
                    echo "========================================="

                    echo "Backend  : http://SERVER-IP:${BACKEND_PROD_PORT}"
                    echo "Frontend : http://SERVER-IP"
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
            echo "===== CLEANING CI ENVIRONMENT ====="
            echo "========================================="

            sh '''
                docker rm -f devops-backend-test 2>/dev/null || true
                docker rm -f devops-backend-ci-db 2>/dev/null || true
                docker rm -f devops-frontend-ci-test 2>/dev/null || true

                docker network rm devops-backend-ci-network 2>/dev/null || true
            '''
        }


        success {

            echo "========================================="
            echo "===== PIPELINE SUCCESS ====="
            echo "========================================="

            echo "All tests passed."
            echo "Backend deployed successfully."
            echo "Frontend deployed successfully."
            echo "PostgreSQL deployed successfully."
        }


        failure {

            echo "========================================="
            echo "===== PIPELINE FAILED ====="
            echo "========================================="

            echo "Check the failed stage above."
        }
    }
}
