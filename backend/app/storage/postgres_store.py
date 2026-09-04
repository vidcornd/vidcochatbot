import psycopg2
from app.config import settings

def get_connection():
    return psycopg2.connect(settings.database_url)

def init_db() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    question TEXT,
                    answer TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS consent (
                    id SERIAL PRIMARY KEY,
                    session_token TEXT,
                    name TEXT NOT NULL,
                    consented_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages (conversation_id)
            """)
        conn.commit()
    finally:
        conn.close()

def save_feedback(conversation_id: str, rating: str, question: str, answer: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO feedback (conversation_id, rating, question, answer) VALUES (%s, %s, %s, %s)",(conversation_id, rating, question, answer))
        conn.commit()
    finally:
        conn.close()

def save_consent(session_token: str | None, name: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO consent (session_token, name) VALUES (%s, %s)",(session_token, name))
        conn.commit()
    finally:
        conn.close()

def save_conversation_message(conversation_id: str, role: str, content: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
                (conversation_id, role, content),
            )
        conn.commit()
    finally:
        conn.close()

def ping_db() -> bool:
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False