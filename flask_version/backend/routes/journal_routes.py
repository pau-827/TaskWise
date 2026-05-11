from flask import Blueprint, request, jsonify
from services.journal_service import reflect_on_entry

journal_routes = Blueprint("journal", __name__)


@journal_routes.route("/journal/reflect", methods=["POST"])
def reflect():
    body      = request.get_json()
    entry_id  = body.get("entry_id")
    content   = body.get("content")
    user_jwt  = body.get("user_jwt")

    if not entry_id or not content:
        return jsonify({ "error": "entry_id and content are required." }), 400

    result, status = reflect_on_entry(entry_id, content, user_jwt)
    return jsonify(result), status
