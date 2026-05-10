from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from supabase import create_client
from utils.supabase_client import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, timezone


def build_classroom_service(access_token):
    creds = Credentials(token=access_token)
    return build("classroom", "v1", credentials=creds)


def fetch_classroom_assignments(access_token):
    service     = build_classroom_service(access_token)
    assignments = []

    courses_result = service.courses().list(courseStates=["ACTIVE"]).execute()
    courses = courses_result.get("courses", [])

    for course in courses:
        course_id   = course["id"]
        course_name = course.get("name", "Unknown Course")
        try:
            cw_result = service.courses().courseWork().list(
                courseId=course_id,
                courseWorkStates=["PUBLISHED"],
                orderBy="dueDate asc",
            ).execute()
            for cw in cw_result.get("courseWork", []):
                due_date = None
                if "dueDate" in cw:
                    d = cw["dueDate"]
                    t = cw.get("dueTime", {})
                    due_date = datetime(
                        d.get("year", 2000), d.get("month", 1), d.get("day", 1),
                        t.get("hours", 0), t.get("minutes", 0),
                        tzinfo=timezone.utc
                    ).isoformat()

                assignments.append({
                    "course_name": course_name,
                    "title":       cw.get("title", "Untitled Assignment"),
                    "description": cw.get("description", ""),
                    "due_date":    due_date,
                    "link":        cw.get("alternateLink", ""),
                })
        except Exception as e:
            print(f"Error fetching coursework for {course_name}: {e}")
            continue

    return assignments


def get_authed_client(user_jwt):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(user_jwt)
    return client


def sync_classroom_to_tasks(access_token, user_id, user_jwt=None):
    assignments = fetch_classroom_assignments(access_token)

    if not assignments:
        return { "synced": 0, "skipped": 0, "message": "No assignments found in Google Classroom." }

    client = get_authed_client(user_jwt) if user_jwt else __import__("utils.supabase_client", fromlist=["supabase"]).supabase

    existing      = client.table("tasks").select("title, due_date").eq("user_id", user_id).execute()
    existing_keys = set((t["title"], t["due_date"]) for t in (existing.data or []))

    to_insert = []
    skipped   = 0

    for a in assignments:
        key = (a["title"], a["due_date"])
        if key in existing_keys:
            skipped += 1
            continue
        to_insert.append({
            "user_id":     user_id,
            "title":       a["title"],
            "description": f"[{a['course_name']}] {a['description']}\n{a['link']}".strip(),
            "category":    "Study",
            "priority":    "medium",
            "status":      "pending",
            "due_date":    a["due_date"],
            "synced_from": "classroom",
        })

    if to_insert:
        client.table("tasks").insert(to_insert).execute()

    return {
        "synced":  len(to_insert),
        "skipped": skipped,
        "message": f"Synced {len(to_insert)} new assignment(s), skipped {skipped} already existing.",
    }


def unsync_classroom_tasks(user_id, user_jwt=None):
    client = get_authed_client(user_jwt) if user_jwt else __import__("utils.supabase_client", fromlist=["supabase"]).supabase

    result = client.table("tasks") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("synced_from", "classroom") \
        .execute()

    deleted = len(result.data) if result.data else 0
    return {
        "deleted": deleted,
        "message": f"Removed {deleted} synced classroom task(s) from TaskWise.",
    }
