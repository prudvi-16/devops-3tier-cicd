import os
from flask import Flask, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "employee_db"),
        user=os.getenv("DB_USER", "devops_user"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )


def init_db():
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    department VARCHAR(100) NOT NULL
                )
            """)

        conn.commit()

    finally:
        conn.close()


@app.route("/")
def home():
    return "Hello from DevOps!"


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()

        return {
            "status": "UP",
            "application": "DevOps Employee Portal",
            "database": "CONNECTED"
        }

    except Exception as error:
        return {
            "status": "DOWN",
            "application": "DevOps Employee Portal",
            "database": "DISCONNECTED",
            "error": str(error)
        }, 500


@app.route("/api")
def api():
    return {
        "message": "DevOps API is working!"
    }


@app.route("/employees", methods=["GET"])
def get_employees():
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, email, department
                FROM employees
                ORDER BY id
            """)

            employees = cursor.fetchall()

        return employees

    finally:
        conn.close()


@app.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json()

    if not data:
        return {"error": "JSON body required"}, 400

    required_fields = ["name", "email", "department"]

    for field in required_fields:
        if field not in data:
            return {"error": f"Missing field: {field}"}, 400

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO employees (name, email, department)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, department
            """, (
                data["name"],
                data["email"],
                data["department"]
            ))

            employee = cursor.fetchone()

        conn.commit()

        return employee, 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"error": "Email already exists"}, 409

    finally:
        conn.close()


@app.route("/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, email, department
                FROM employees
                WHERE id = %s
            """, (employee_id,))

            employee = cursor.fetchone()

        if not employee:
            return {"error": "Employee not found"}, 404

        return employee

    finally:
        conn.close()


@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json()

    if not data:
        return {"error": "JSON body required"}, 400

    required_fields = ["name", "email", "department"]

    for field in required_fields:
        if field not in data:
            return {"error": f"Missing field: {field}"}, 400

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                UPDATE employees
                SET name = %s,
                    email = %s,
                    department = %s
                WHERE id = %s
                RETURNING id, name, email, department
            """, (
                data["name"],
                data["email"],
                data["department"],
                employee_id
            ))

            employee = cursor.fetchone()

        if not employee:
            conn.rollback()
            return {"error": "Employee not found"}, 404

        conn.commit()

        return employee

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"error": "Email already exists"}, 409

    finally:
        conn.close()


@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM employees
                WHERE id = %s
                RETURNING id
            """, (employee_id,))

            deleted = cursor.fetchone()

        if not deleted:
            conn.rollback()
            return {"error": "Employee not found"}, 404

        conn.commit()

        return {
            "message": "Employee deleted successfully",
            "id": employee_id
        }

    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
