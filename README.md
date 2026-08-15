# DevOps 3-Tier CI/CD Project

A complete 3-tier application demonstrating an automated DevOps workflow using AWS, Docker, Jenkins, GitHub, PostgreSQL, and a Flask backend.

## Architecture

GitHub
   |
   | Webhook
   v
Jenkins
   |
   +----------------------+
   |                      |
   v                      v
Backend Docker        Frontend Docker
   |                      |
   v                      |
PostgreSQL <-------------+

## Technology Stack

- AWS EC2
- Linux
- Git & GitHub
- Jenkins
- Docker
- Docker Compose
- Python
- Flask
- PostgreSQL
- HTML / CSS / JavaScript

## Application Components

### Backend

Flask REST API running inside Docker.

Backend endpoints:

- GET /health
- GET /api
- GET /employees
- POST /employees
- GET /employees/{id}
- PUT /employees/{id}
- DELETE /employees/{id}

Backend container listens internally on port 5000 and is exposed through port 8080.

### Database

PostgreSQL 16 running as a Docker container.

Database:

- Database: employee_db
- User: devops_user

Employee information is stored in the PostgreSQL database.

### Frontend

Static frontend application served through an Nginx Docker container.

The frontend communicates with the backend API through port 8080.

## CI/CD Pipeline

Jenkins automatically performs the following workflow:

1. Checkout source code from GitHub
2. Test backend Python application
3. Build backend Docker image
4. Test backend container
5. Push backend image to Docker Hub
6. Prepare PostgreSQL environment
7. Deploy backend and PostgreSQL
8. Perform backend health checks
9. Test frontend
10. Build frontend Docker image
11. Test frontend container
12. Push frontend image to Docker Hub
13. Deploy frontend
14. Perform frontend health checks
15. Perform final system verification

## Backend Verification

Health check:

    curl http://SERVER-IP:8080/health

Example successful response:

    {
      "application": "DevOps Employee Portal",
      "database": "CONNECTED",
      "status": "UP"
    }

## Employee CRUD

Create employee:

    curl -X POST http://SERVER-IP:8080/employees \
    -H "Content-Type: application/json" \
    -d '{"name":"Prudvi Kumar","email":"prudvi@example.com","department":"DevOps"}'

Get all employees:

    curl http://SERVER-IP:8080/employees

Update employee:

    curl -X PUT http://SERVER-IP:8080/employees/1 \
    -H "Content-Type: application/json" \
    -d '{"name":"Prudvi Kumar","email":"prudvi@example.com","department":"Cloud DevOps"}'

Delete employee:

    curl -X DELETE http://SERVER-IP:8080/employees/1

## Docker Images

Backend:

    prudvik2026/devops-backend

Frontend:

    prudvik2026/devops-frontend

## Current Project Status

- GitHub repository: Working
- Jenkins pipeline: Working
- Backend: Working
- PostgreSQL: Working
- Employee CRUD API: Working
- Frontend: Working
- Docker deployment: Working
- CI/CD pipeline: Successful
- Final system verification: Successful

## Project Objective

This project demonstrates practical knowledge of:

- Linux administration
- AWS EC2
- Git/GitHub
- Docker
- Docker Compose
- Jenkins CI/CD
- PostgreSQL
- REST APIs
- Containerized application deployment
- Automated testing
- Automated deployment



