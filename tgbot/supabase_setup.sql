-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql)
-- to create the sessions table for the String Session Bot.

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
