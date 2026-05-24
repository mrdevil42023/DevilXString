import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def init_db():
    """Create sessions table if it doesn't exist via Supabase SQL."""
    try:
        supabase.table("sessions").select("id").limit(1).execute()
    except Exception:
        pass


def save_session(user_id: int, username: str, session_string: str, session_type: str):
    try:
        existing = supabase.table("sessions").select("id").eq("user_id", user_id).eq("session_type", session_type).execute()
        if existing.data:
            supabase.table("sessions").update({
                "session_string": session_string,
                "username": username,
            }).eq("user_id", user_id).eq("session_type", session_type).execute()
        else:
            supabase.table("sessions").insert({
                "user_id": user_id,
                "username": username or "",
                "session_string": session_string,
                "session_type": session_type,
            }).execute()
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False


def get_user_sessions(user_id: int):
    try:
        result = supabase.table("sessions").select("*").eq("user_id", user_id).execute()
        return result.data or []
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        return []


def get_all_sessions():
    try:
        result = supabase.table("sessions").select("*").execute()
        return result.data or []
    except Exception as e:
        print(f"Error fetching all sessions: {e}")
        return []
