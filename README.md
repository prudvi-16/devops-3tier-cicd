# DevOps 3-Tier CI/CD Project

A simple 3-tier Employee Management application that I built to practice and demonstrate real-world DevOps and Cloud concepts.

The main goal of this project was not just to run an application, but to automate the complete process from source code → testing → Docker image → Docker Hub → deployment on AWS EC2 using Jenkins.

---

## Project Overview

In this project, I built an Employee Management application with a frontend, Flask backend, and PostgreSQL database.

The application is containerized using Docker and the containers are managed using Docker Compose.

Jenkins is used to automate the CI/CD process. Whenever the pipeline runs, Jenkins checks the application, builds the Docker image, performs container and API tests, pushes the image to Docker Hub, and deploys the application on an AWS EC2 instance.

### In simple terms:

```text
Developer
    |
    | Push code
    v
GitHub
    |
    | Jenkins pulls code
    v
Jenkins
    |
    +--> Test Application
    |
    +--> Build Docker Image
    |
    +--> Run Container Tests
    |
    +--> Test APIs
    |
    +--> Push Image to Docker Hub
    |
    +--> Deploy Application
    |
    v
AWS EC2
    |
    +--> Frontend
    |
    +--> Flask Backend
    |
    +--> PostgreSQL
What I Used
AWS EC2
Amazon Linux
Linux / Bash
Git
GitHub
Jenkins
Docker
Docker Compose
Python
Flask
PostgreSQL
Docker Hub
SSH
Architecture

The application consists of three main layers.

1. Frontend

The frontend provides the user interface for the Employee Management application.

It runs inside a Docker container.

2. Backend

The backend is developed using Python Flask.

It provides REST APIs for:

Health checking
Application status
Employee management
Database communication

The Flask application listens internally on port 5000.

The Docker deployment exposes it through:

EC2 Port 8080 → Container Port 5000
3. Database

PostgreSQL is used as the database.

The database runs in its own Docker container and communicates with the backend through the Docker Compose network.

The PostgreSQL port is not exposed directly to the host. This keeps database access inside the Docker network.

Architecture Diagram
                         GitHub
                           |
                           | SSH
                           v
                     +-----------+
                     |  Jenkins  |
                     +-----+-----+
                           |
                     CI/CD Pipeline
                           |
              +------------+-------------+
              |            |             |
              v            v             v
          Test Code    Build Image    Container Test
              |            |             |
              +------------+-------------+
                           |
                           v
                     Docker Hub
                           |
                           | Pull latest image
                           v
                    +-------------+
                    |   AWS EC2   |
                    +------+------+
                           |
                 +---------+---------+
                 |                   |
                 v                   v
          +-------------+     +-------------+
          |   Frontend  |     |   Backend   |
          |  Container  | --> | Flask       |
          +-------------+     | Container   |
                              +------+------+
                                     |
                                     v
                              +-------------+
                              | PostgreSQL  |
                              |  Container  |
                              +-------------+
Project Structure

The repository is organized roughly like this:

devops-3tier-cicd/
│
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   ├── compose.yaml
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── ...
│   └── Dockerfile
│
└── Jenkinsfile

.env contains environment-specific database credentials and should not be committed to GitHub. A .env.example file can be used for documentation instead.

Backend

The backend is a Flask application.

It provides APIs for the Employee Management system.

Some of the endpoints used during testing were:

GET /health
GET /api
GET /employees
POST /employees
Health Endpoint
GET /health

Example response:

{
  "application": "DevOps Employee Portal",
  "database": "CONNECTED",
  "status": "UP"
}

This endpoint was particularly useful for checking whether both the Flask application and PostgreSQL connection were working.

Docker

Docker is used to package the application and its dependencies into containers.

The backend Docker image contains:

Python
Flask
Application code
Python dependencies

The PostgreSQL database uses the official PostgreSQL Alpine image.

The backend image is published to Docker Hub as:

prudvik2026/devops-backend

The pipeline publishes both:

prudvik2026/devops-backend:test

and:

prudvik2026/devops-backend:latest
Docker Compose

Docker Compose is used to run the backend and PostgreSQL together.

The main Compose services are:

backend
db

The backend depends on PostgreSQL becoming healthy before the backend starts.

The database also uses a named Docker volume:

postgres_data

This allows PostgreSQL data to persist beyond the lifecycle of the database container.

Jenkins CI/CD Pipeline

Jenkins is the main automation component of this project.

The pipeline is defined in:

Jenkinsfile

The pipeline performs several stages instead of simply building the application.

Pipeline Flow
Checkout Source
       |
       v
Backend Test
       |
       v
Backend Docker Build
       |
       v
Backend Container Test
       |
       v
Backend Docker Push
       |
       v
Prepare Database Environment
       |
       v
Deploy Backend + PostgreSQL
       |
       v
Backend Health Check
       |
       v
Frontend Test
       |
       v
Frontend Docker Build
       |
       v
Frontend Container Test
       |
       v
Frontend Docker Push
       |
       v
Deploy Frontend
       |
       v
Frontend Health Check
       |
       v
Final System Verification
What the Pipeline Tests

I wanted the pipeline to test more than just whether the Docker image could be built.

1. Python Application Test

Jenkins first checks whether the Python application can be compiled successfully.

python3 -m py_compile app.py
2. Docker Build

The backend Docker image is built:

docker build -t prudvik2026/devops-backend:test backend
3. Temporary PostgreSQL Environment

For backend integration testing, Jenkins creates a temporary PostgreSQL container.

It also creates a temporary Docker network so the backend can communicate with PostgreSQL.

4. PostgreSQL Health Check

Jenkins waits until PostgreSQL becomes ready using:

pg_isready

This prevents the backend tests from running before the database is ready.

5. Backend Container Test

The backend container is started and checked to make sure it is actually running.

The pipeline then checks the application logs and container status.

6. Health API Test

Jenkins calls:

/health

and expects:

HTTP 200

It also verifies that the database status is:

CONNECTED
7. API Test

The pipeline checks:

/api

and expects:

HTTP 200
8. Employee CREATE Test

The pipeline creates a test employee using:

POST /employees

Example test data:

{
  "name": "Jenkins Test User",
  "email": "jenkins-test@example.com",
  "department": "DevOps"
}

The API returned:

HTTP 201
9. Employee GET Test

The pipeline then retrieves the employees using:

GET /employees

The request returned:

HTTP 200

This gave me confidence that the backend was not only running but was also able to communicate with PostgreSQL.

Docker Hub

After the tests pass, Jenkins logs into Docker Hub and pushes the backend image.

The image is available as:

prudvik2026/devops-backend:latest

The deployment server then pulls the latest image before starting the application.

This gives the pipeline a simple image-based deployment flow:

Jenkins
   |
   v
Build Image
   |
   v
Test Image
   |
   v
Push to Docker Hub
   |
   v
Pull Image on EC2
   |
   v
Deploy
AWS EC2 Deployment

The application is deployed on an AWS EC2 Linux instance.

The EC2 instance acts as the deployment server as well as the Jenkins/Docker host used in this project.

The backend is exposed through:

EC2:8080
     |
     v
Docker:5000

PostgreSQL remains available through the internal Docker network rather than being exposed directly to the Internet.

Environment Variables

Database configuration is supplied through environment variables.

Example:

POSTGRES_DB=employee_db
POSTGRES_USER=devops_user
POSTGRES_PASSWORD=<your-password>

The actual .env file should not be committed to a public GitHub repository.

For a public project, I would use:

.env.example

and keep the real credentials on the deployment server or in a proper secrets-management system.

Troubleshooting During the Project

One of the useful problems I faced during deployment was a Docker port conflict.

Jenkins initially failed during deployment with:

Bind for 0.0.0.0:8080 failed:
port is already allocated

I checked the port using:

sudo ss -ltnp | grep ':8080'

and found that a docker-proxy process was holding the port.

I also checked:

sudo lsof -nP -iTCP:8080 -sTCP:LISTEN

After cleaning up the old Docker Compose resources and restarting Docker:

sudo systemctl restart docker

I verified:

Port 8080 is FREE

The application was then started successfully using Docker Compose.

This was a good practical example of troubleshooting a deployment issue rather than simply restarting Jenkins.

Final Verification

After deployment, I manually verified the backend.

Health
curl -i http://127.0.0.1:8080/health

Result:

HTTP/1.1 200 OK

Response:

{
  "application": "DevOps Employee Portal",
  "database": "CONNECTED",
  "status": "UP"
}
API
curl -i http://127.0.0.1:8080/api

Result:

HTTP/1.1 200 OK
Employees
curl -i http://127.0.0.1:8080/employees

Result:

HTTP/1.1 200 OK
Final Jenkins Result

The final Jenkins pipeline completed successfully.

All tests passed.
Backend deployed successfully.
Frontend deployed successfully.
PostgreSQL deployed successfully.


Finished: SUCCESS

This was the final confirmation that the CI/CD workflow was working end-to-end.

What I Learned From This Project

This project helped me get practical experience with several DevOps concepts.

Linux
Managing services with systemctl
Checking processes
Checking ports
Reading logs
Troubleshooting services
Working with an EC2 Linux server
Git & GitHub
Git repositories
Branches
Remote repositories
SSH authentication
Jenkins SCM integration
Docker
Writing Dockerfiles
Building images
Running containers
Container networking
Port mapping
Docker volumes
Container health checks
Docker Compose
Multi-container applications
Service dependencies
Environment variables
Persistent volumes
Database networking
Jenkins
Pipeline creation
Jenkinsfile
Credentials
GitHub integration
Automated testing
Docker builds
Docker Hub publishing
Automated deployment
AWS
EC2
Linux server administration
Application deployment
Network ports
Service troubleshooting
Future Improvements

There are several things I would improve if I continue developing this project.

Use Nginx as a reverse proxy
Add HTTPS using a domain and TLS certificate
Use Gunicorn instead of Flask's development server
Store secrets in AWS Secrets Manager or another secrets-management solution
Add automated rollback
Add monitoring and centralized logging
Add unit tests using pytest
Add better frontend/backend separation
Use a dedicated production database
Add infrastructure automation using Terraform
Add AWS load balancing for a more production-oriented deployment
Project Outcome

The main objective of this project was to understand how different DevOps tools work together instead of learning each tool independently.

The final workflow is:

GitHub
   ↓
Jenkins
   ↓
Automated Tests
   ↓
Docker Build
   ↓
Container Tests
   ↓
Docker Hub
   ↓
AWS EC2
   ↓
Docker Compose
   ↓
Frontend + Flask + PostgreSQL
   ↓
Health & API Verification

The project successfully demonstrates a complete CI/CD workflow for a containerized application.

Author

Prudvi Kumar

DevOps / Cloud Engineering

Skills demonstrated in this project:

Linux
AWS
Git
GitHub
Docker
Docker Compose
Jenkins
CI/CD
Python
Flask
PostgreSQL
Docker Hub
