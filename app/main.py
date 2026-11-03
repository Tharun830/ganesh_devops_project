import os
import platform
import socket
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request

START_TIME = time.time()

def create_app():
    app = Flask(__name__)
    app.config["APP_NAME"] = os.getenv("APP_NAME", "Ganesh DevOps Project")
    app.config["APP_ENV"] = os.getenv("APP_ENV", "production")
    app.config["APP_VERSION"] = os.getenv("APP_VERSION", "1.0.0")

    # In-memory store for sample DevOps deployment logs/tasks
    tasks_db = [
        {
            "id": 1,
            "title": "Dockerize Application",
            "status": "Completed",
            "category": "Containerization",
            "timestamp": "2026-11-03 12:00:00"
        },
        {
            "id": 2,
            "title": "Jenkins Pipeline Configuration",
            "status": "Completed",
            "category": "CI/CD",
            "timestamp": "2026-11-03 12:30:00"
        },
        {
            "id": 3,
            "title": "Automated Unit Tests & Quality Gate",
            "status": "In Progress",
            "category": "Testing",
            "timestamp": "2026-11-03 13:00:00"
        }
    ]

    def get_system_stats():
        uptime_seconds = int(time.time() - START_TIME)
        hours, rem = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        uptime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

        return {
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "uptime_seconds": uptime_seconds,
            "uptime_human": uptime_str,
            "is_containerized": os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "true",
            "server_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    @app.route("/")
    def index():
        stats = get_system_stats()
        return render_template(
            "index.html",
            app_name=app.config["APP_NAME"],
            app_env=app.config["APP_ENV"],
            app_version=app.config["APP_VERSION"],
            stats=stats,
            tasks=tasks_db
        )

    @app.route("/health")
    def health():
        return jsonify({
            "status": "UP",
            "service": "ganesh_devops_project",
            "version": app.config["APP_VERSION"],
            "environment": app.config["APP_ENV"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "web_server": "healthy",
                "system_runtime": "operational"
            }
        }), 200

    @app.route("/api/metrics")
    def metrics():
        stats = get_system_stats()
        return jsonify({
            "service": "ganesh_devops_project",
            "status": "healthy",
            "metrics": stats
        }), 200

    @app.route("/api/tasks", methods=["GET", "POST"])
    def tasks():
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            title = data.get("title", "").strip()
            category = data.get("category", "General").strip()

            if not title:
                return jsonify({"error": "Task title is required"}), 400

            new_task = {
                "id": len(tasks_db) + 1,
                "title": title,
                "status": data.get("status", "Pending"),
                "category": category,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }
            tasks_db.append(new_task)
            return jsonify({"message": "Task added successfully", "task": new_task}), 201

        return jsonify({"tasks": tasks_db, "count": len(tasks_db)}), 200

    @app.route("/api/info")
    def info():
        return jsonify({
            "project_name": "Ganesh DevOps Project",
            "description": "Enterprise-ready DevOps showcase with Docker, Jenkins CI/CD, and automated health checks.",
            "version": app.config["APP_VERSION"],
            "stack": ["Python", "Flask", "Docker", "Jenkins", "GitHub Actions"]
        }), 200

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
