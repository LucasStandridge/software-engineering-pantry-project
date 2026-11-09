import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/health")
def health():
    return jsonify(status="ok")

#database connection and health
@app.route("/api/database-health", methods=["GET"])
def database_health():
    try:
        with psycopg.connect(
            os.environ["DATABASE_URL"],
            sslmode="require",
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        return jsonify(
            status="connected",
            database="Supabase PostgreSQL",
            test_result=result[0]
        ), 200
    except Exception:
        app.logger.exception("Database connection failed")
        return jsonify(
            status="error",
            message="Database connection failed."
        ), 500