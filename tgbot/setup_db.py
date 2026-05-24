"""Run this once to create the sessions table in Supabase."""
import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username TEXT DEFAULT '',
    session_string TEXT NOT NULL,
    session_type TEXT NOT NULL CHECK (session_type IN ('pyrogram', 'telethon')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_type ON sessions(user_id, session_type);
"""

try:
    result = client.rpc("exec_sql", {"sql": CREATE_TABLE_SQL}).execute()
    print("Table created successfully!")
except Exception as e:
    print(f"Note: {e}")
    print("Please create the table manually in Supabase SQL editor:")
    print(CREATE_TABLE_SQL)
