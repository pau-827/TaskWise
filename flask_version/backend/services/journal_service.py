import os
from groq import Groq
from dotenv import load_dotenv
from utils.supabase_client import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MOOD_OPTIONS = ["Happy", "Calm", "Neutral", "Sad", "Anxious", "Angry"]

SYSTEM_PROMPT = """You are a warm, empathetic journaling companion named Sage.
When a user shares a journal entry with you, you:
1. Respond with a short, genuine, empathetic reflection (2-4 sentences). 
   Be conversational, kind, and insightful — not clinical or robotic.
2. Suggest ONE mood from this exact list based on the emotional tone of the entry:
   Happy, Calm, Neutral, Sad, Anxious, Angry

You MUST respond in this exact JSON format and nothing else:
{
  "reflection": "Your empathetic response here.",
  "mood": "One mood from the list"
}"""


def get_authed_client(user_jwt):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.auth(user_jwt)
    return client


def reflect_on_entry(entry_id, content, user_jwt):
    if not content or not content.strip():
        return { "error": "Entry content is empty." }, 400

    # Call Groq
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                { "role": "system",  "content": SYSTEM_PROMPT },
                { "role": "user",    "content": f"Here is my journal entry:\n\n{content.strip()}" },
            ],
            temperature=0.7,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()

        # Parse JSON response
        import json
        parsed = json.loads(raw)
        reflection = parsed.get("reflection", "").strip()
        ai_mood    = parsed.get("mood", "Neutral").strip()

        # Validate mood is one of our options
        if ai_mood not in MOOD_OPTIONS:
            ai_mood = "Neutral"

    except Exception as e:
        print(f"Groq error: {e}")
        return { "error": f"AI reflection failed: {str(e)}" }, 500

    # Save to Supabase
    try:
        client = get_authed_client(user_jwt)
        client.table("journal_entries").update({
            "ai_reflection": reflection,
            "ai_mood":       ai_mood,
        }).eq("id", entry_id).execute()
    except Exception as e:
        print(f"Supabase save error: {e}")
        # Still return the result even if save fails
        return { "reflection": reflection, "mood": ai_mood }, 200

    return { "reflection": reflection, "mood": ai_mood }, 200