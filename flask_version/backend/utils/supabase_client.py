import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

from utils.supabase_client import supabase

# Test connection
data = supabase.table("tasks").select("*").execute()
print("Supabase connected:", data)