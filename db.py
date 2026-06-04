import sqlite3
from datetime import datetime
import streamlit as st

@st.cache_resource  
def init_db():
    conn = sqlite3.connect('professors.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS professors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            language TEXT NOT NULL,
            provider TEXT NOT NULL,
            time TEXT,
            llm_text TEXT NOT NULL
        )
    """)
    return conn

def save_professor(conn, author, llm_text, language, provider):
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO professors (author_id, name, language, provider, time, llm_text) VALUES (?, ?, ?, ?, ?, ?)",
            (author['authorId'], author['name'], language, provider, datetime.now().isoformat(), llm_text)
        )

def search_professor(conn, id, language):
    result = conn.execute("SELECT 1 FROM professors WHERE author_id = ? AND language = ?", (id, language)).fetchone()
    return True if result else False

def get_professor(author_id, conn):
    return conn.execute("SELECT * FROM professors WHERE author_id = ?", (author_id,)).fetchone()