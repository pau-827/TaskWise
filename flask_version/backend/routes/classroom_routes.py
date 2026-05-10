from flask import Blueprint, request, jsonify
from services.classroom_service import sync_classroom_to_tasks, unsync_classroom_tasks

classroom_routes = Blueprint("classroom", __name__)


@classroom_routes.route("/classroom/sync", methods=["POST"])
def sync_classroom():
    body         = request.get_json()
    access_token = body.get("access_token")
    user_id      = body.get("user_id")
    user_jwt     = body.get("user_jwt")

    if not access_token or not user_id:
        return jsonify({ "error": "access_token and user_id are required." }), 400

    try:
        result = sync_classroom_to_tasks(access_token, user_id, user_jwt)
        return jsonify(result), 200
    except Exception as e:
        print(f"Classroom sync error: {e}")
        return jsonify({ "error": str(e) }), 500


@classroom_routes.route("/classroom/unsync", methods=["DELETE"])
def unsync_classroom():
    body     = request.get_json()
    user_id  = body.get("user_id")
    user_jwt = body.get("user_jwt")

    if not user_id:
        return jsonify({ "error": "user_id is required." }), 400

    try:
        result = unsync_classroom_tasks(user_id, user_jwt)
        return jsonify(result), 200
    except Exception as e:
        print(f"Classroom unsync error: {e}")
        return jsonify({ "error": str(e) }), 500
