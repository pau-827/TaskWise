from flask import Blueprint, jsonify
from services.task_service import get_tasks

task_routes = Blueprint("tasks", __name__)

@task_routes.route("/tasks", methods=["GET"])
def tasks():
    data = get_tasks()
    return jsonify(data)