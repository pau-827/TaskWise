from utils.supabase_client import supabase

def get_tasks():
    response = supabase.table("tasks").select("*").execute()
    return response.data