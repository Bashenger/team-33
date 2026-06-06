import sqlite3

DATABASE_NAME = "chat_memory.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # Session Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        session_id TEXT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id)
            REFERENCES sessions(session_id)
    )
    """)

    # User Preferences Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        preference_key TEXT,
        preference_value TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_session(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO sessions(session_id)
    VALUES(?)
    """, (session_id,))

    conn.commit()
    conn.close()


def save_message(session_id, role, message):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages(
        session_id,
        role,
        message
    )
    VALUES (?, ?, ?)
    """, (
        session_id,
        role,
        message
    ))

    conn.commit()
    conn.close()


def get_chat_history(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message
    FROM messages
    WHERE session_id = ?
    ORDER BY id
    """, (session_id,))

    history = cursor.fetchall()

    conn.close()

    return history


def save_preference(
    session_id,
    preference_key,
    preference_value
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM user_preferences
    WHERE session_id = ?
    AND preference_key = ?
    """, (
        session_id,
        preference_key
    ))

    cursor.execute("""
    INSERT INTO user_preferences(
        session_id,
        preference_key,
        preference_value
    )
    VALUES (?, ?, ?)
    """, (
        session_id,
        preference_key,
        preference_value
    ))

    conn.commit()
    conn.close()


def get_preferences(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT preference_key,
           preference_value
    FROM user_preferences
    WHERE session_id = ?
    """, (session_id,))

    preferences = cursor.fetchall()

    conn.close()

    return preferences


def get_recent_messages(session_id, limit=5):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message
    FROM messages
    WHERE session_id = ?
    ORDER BY id DESC
    LIMIT ?
    """, (session_id, limit))

    messages = cursor.fetchall()

    conn.close()

    return list(reversed(messages))


def get_session_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM sessions
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_message_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM messages
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


def delete_session(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM messages
    WHERE session_id = ?
    """, (session_id,))

    cursor.execute("""
    DELETE FROM user_preferences
    WHERE session_id = ?
    """, (session_id,))

    cursor.execute("""
    DELETE FROM sessions
    WHERE session_id = ?
    """, (session_id,))

    conn.commit()
    conn.close()