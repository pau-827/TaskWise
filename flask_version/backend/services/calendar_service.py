from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from supabase import create_client
from utils.supabase_client import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, timezone, timedelta


def build_calendar_service(access_token):
    creds = Credentials(token=access_token)
    return build("calendar", "v3", credentials=creds)


def get_authed_client(user_jwt):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(user_jwt)
    return client


def fetch_calendar_events(access_token):
    service = build_calendar_service(access_token)
    events  = []

    # Fetch events from now up to 3 months ahead
    now       = datetime.now(timezone.utc)
    time_min  = now.isoformat()
    time_max  = (now + timedelta(days=90)).isoformat()

    # Get all user calendars
    cal_list = service.calendarList().list().execute()
    calendars = cal_list.get("items", [])

    for cal in calendars:
        cal_id   = cal["id"]
        cal_name = cal.get("summary", "My Calendar")

        try:
            events_result = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                maxResults=50,
            ).execute()

            for event in events_result.get("items", []):
                # Skip all-day events with no time (optional: include them)
                start = event.get("start", {})
                due_date = None

                if "dateTime" in start:
                    due_date = start["dateTime"]
                elif "date" in start:
                    # All-day event — use noon UTC of that day
                    due_date = f"{start['date']}T12:00:00+00:00"

                events.append({
                    "cal_name":    cal_name,
                    "title":       event.get("summary", "Untitled Event"),
                    "description": event.get("description", ""),
                    "due_date":    due_date,
                    "link":        event.get("htmlLink", ""),
                })
        except Exception as e:
            print(f"Error fetching events from {cal_name}: {e}")
            continue

    return events


def sync_calendar_to_tasks(access_token, user_id, user_jwt=None):
    events = fetch_calendar_events(access_token)

    if not events:
        return { "synced": 0, "skipped": 0, "message": "No upcoming events found in Google Calendar." }

    client = get_authed_client(user_jwt) if user_jwt else __import__("utils.supabase_client", fromlist=["supabase"]).supabase

    # Avoid duplicates
    existing      = client.table("tasks").select("title, due_date").eq("user_id", user_id).execute()
    existing_keys = set((t["title"], t["due_date"]) for t in (existing.data or []))

    to_insert = []
    skipped   = 0

    for e in events:
        key = (e["title"], e["due_date"])
        if key in existing_keys:
            skipped += 1
            continue
        to_insert.append({
            "user_id":     user_id,
            "title":       e["title"],
            "description": f"[{e['cal_name']}] {e['description']}\n{e['link']}".strip(),
            "category":    "Personal",
            "priority":    "medium",
            "status":      "pending",
            "due_date":    e["due_date"],
            "synced_from": "calendar",
        })

    if to_insert:
        client.table("tasks").insert(to_insert).execute()

    return {
        "synced":  len(to_insert),
        "skipped": skipped,
        "message": f"Synced {len(to_insert)} new event(s), skipped {skipped} already existing.",
    }


def unsync_calendar_tasks(user_id, user_jwt=None):
    client = get_authed_client(user_jwt) if user_jwt else __import__("utils.supabase_client", fromlist=["supabase"]).supabase

    result  = client.table("tasks").delete() \
        .eq("user_id", user_id) \
        .eq("synced_from", "calendar") \
        .execute()

    deleted = len(result.data) if result.data else 0
    return {
        "deleted": deleted,
        "message": f"Removed {deleted} synced calendar event(s) from TaskWise.",
    }
