import mysql.connector
import streamlit as st

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",   
            user="root",
            password="",         
            database="ai_chat",
            port=3306,          
            autocommit=True
        )

       
        return conn

    except mysql.connector.Error as err:
        st.error(f"❌ MySQL connection failed: {err}")
        return None
def create_chat_session(title="New Chat"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (title) VALUES (%s)", (title,))
    conn.commit()
    chat_id = cursor.lastrowid
    conn.close()
    return chat_id


def update_chat_title(chat_id, new_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_sessions SET title=%s WHERE id=%s", (new_title, chat_id))
    conn.commit()
    conn.close()
