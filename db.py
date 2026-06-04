import sqlite3
import json
from datetime import datetime
import streamlit as st

@st.cache_resource
def init_db():
    conn = sqlite3.connect('professors.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
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
            provider TEXT NOT NULL
        );
    """)
    return conn

def save_papers(conn, author, papers):
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO professor_papers (author_id, name, papers_json, time) VALUES (?, ?, ?, ?)",
            (author['authorId'], author['name'], json.dumps(papers), datetime.now().isoformat())
        )

def get_papers_cache(conn, author_id):
    row = conn.execute("SELECT papers_json FROM professor_papers WHERE author_id = ?", (author_id,)).fetchone()
    return json.loads(row["papers_json"]) if row else None

def create_get_user(conn, username):
    with conn:
        conn.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    return conn.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()['user_id']
    
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
    return row['analysis_text'] if row else None