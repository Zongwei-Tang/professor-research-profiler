import json, os
from datetime import datetime
import streamlit as st
import libsql
from dotenv import load_dotenv

load_dotenv()
@st.cache_resource
def init_db():
    conn = libsql.connect(database=os.environ.get('TURSO_DB_URL'), auth_token=os.environ.get('TURSO_DB_TOKENS'))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS professor_papers(
            author_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            papers_json TEXT NOT NULL,
            time TEXT
        );
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS analyses(
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            analysis_text TEXT NOT NULL,
            time TEXT,
            interest TEXT NOT NULL,
            language TEXT NOT NULL,
            provider TEXT NOT NULL,
            UNIQUE(user_id, author_id, interest, language, provider)
        );
    """)
    return conn

def save_papers(conn, author, papers):
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO professor_papers (author_id, name, papers_json, time) VALUES (?, ?, ?, ?)",
            (author['authorId'], author['name'], json.dumps(papers), datetime.now().isoformat())
        )

def get_papers_cache_and_time(conn, author_id):
    row = conn.execute("SELECT papers_json, time FROM professor_papers WHERE author_id = ?", (author_id,)).fetchone()
    return [json.loads(row[0]), row[1]] if row else None

def create_get_user(conn, username):
    with conn:
        conn.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    return conn.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()[0]
    
def save_analysis(conn, user_id, author_id, author_name, analysis_text, interest, language, provider):
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO analyses (user_id, author_id, author_name, analysis_text, time, interest, language, provider) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, author_id, author_name, analysis_text, datetime.now().isoformat(), interest, language, provider)
        )

def get_user_analysis_history(conn, user_id):
    return conn.execute("SELECT * FROM analyses WHERE user_id = ?", (user_id,)).fetchall()

def get_one_history(conn, user_id, author_id, interest, language, provider):
    row = conn.execute("SELECT * FROM analyses WHERE user_id = ? AND author_id = ? AND interest = ? AND language = ? AND provider = ?", (user_id, author_id, interest, language, provider)).fetchone()
    return row[4] if row else None