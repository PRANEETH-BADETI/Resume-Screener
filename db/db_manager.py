import psycopg2
import streamlit as st
import json
import uuid


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=st.secrets["database"]["DB_NAME"],
            user=st.secrets["database"]["DB_USER"],
            password=st.secrets["database"]["DB_PASSWORD"],
            host=st.secrets["database"]["DB_HOST"],
            port=st.secrets["database"]["DB_PORT"]
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def save_user_to_db(user_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING;",
                    (user_id,)
                )
            conn.commit()
        except Exception as e:
            st.error(f"Error saving user to database: {e}")
        finally:
            if conn:
                conn.close()


def save_screening_session(user_id, job_desc_text, ranked_candidates):
    conn = get_db_connection()
    if conn:
        try:
            save_user_to_db(user_id)
            with conn.cursor() as cur:
                session_id = str(uuid.uuid4())

                saveable_candidates = [
                    {"filename": c['filename'], "score": c['score'], "explanation": c['explanation'],
                     "file_path": c['file_path']}
                    for c in ranked_candidates
                ]

                cur.execute(
                    """
                    INSERT INTO screening_sessions (session_id, user_id, job_description, ranked_resumes, created_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    (session_id, user_id, job_desc_text, json.dumps(saveable_candidates))
                )
            conn.commit()
        except Exception as e:
            st.error(f"Error saving screening session: {e}")
        finally:
            if conn:
                conn.close()


def get_screening_sessions(user_id):
    conn = get_db_connection()
    sessions = []
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT session_id, job_description, ranked_resumes, created_at FROM screening_sessions WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,)
                )
                sessions = cur.fetchall()
        except Exception as e:
            st.error(f"Error retrieving screening sessions: {e}")
        finally:
            if conn:
                conn.close()
    return [(s[0], s[1], s[2], s[3]) for s in sessions]