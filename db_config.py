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

        # Show connection info for debugging
        st.info(f"🔌 Connected to {conn.server_host}:{conn.server_port} | DB: {conn.database}")
        return conn

    except mysql.connector.Error as err:
        st.error(f"❌ MySQL connection failed: {err}")
        return None
