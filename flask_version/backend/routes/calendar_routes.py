from flask import Blueprint, request, jsonify
from services.calendar_service import sync_calendar_to_tasks, unsync_calendar_tasks

calendar_routes = Blueprint("calendar", __name__)


@calendar_routes.route("/gcalendar/sync", methods=["POST"])
def sync_calendar():
    body         = request.get_json()
    access_token = body.get("access_token")
    user_id      = body.get("user_id")
    user_jwt     = body.get("user_jwt")

    if not access_token or not user_id:
        return jsonify({ "error": "access_token and user_id are required." }), 400

    try:
        result = sync_calendar_to_tasks(access_token, user_id, user_jwt)
        return jsonify(result), 200
    except Exception as e:
        print(f"Calendar sync error: {e}")
        return jsonify({ "error": str(e) }), 500


@calendar_routes.route("/gcalendar/unsync", methods=["DELETE"])
def unsync_calendar():
    body     = request.get_json()
    user_id  = body.get("user_id")
    user_jwt = body.get("user_jwt")

    if not user_id:
        return jsonify({ "error": "user_id is required." }), 400

    try:
        result = unsync_calendar_tasks(user_id, user_jwt)
        return jsonify(result), 200
    except Exception as e:
        print(f"Calendar unsync error: {e}")
        return jsonify({ "error": str(e) }), 500
