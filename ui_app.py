import streamlit as st
from chat_logic import get_ai_response, generate_chat_title
from db_config import get_connection, create_chat_session, update_chat_title
from rag_engine import chunk_text, build_index, search_similar
import io
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="AI Chat App", page_icon="🤖", layout="wide")
st.title("🤖 AI Chat Application")
st.caption("Powered by Google Gemini 2.0 Flash + MySQL (XAMPP) + RAG System")
# =========================================================
# 🧱 SIDEBAR - Chat List with Search + New Chat on Top
# =========================================================
st.sidebar.markdown("<h4 style='margin-bottom:10px;'>💬 Chats</h4>", unsafe_allow_html=True)

# --- Search bar ---
search_query = st.sidebar.text_input("🔍 Search chats", placeholder="Type to filter...")

# --- New chat button on top ---
if st.sidebar.button("📝 New Chat", use_container_width=True):
    new_chat_id = create_chat_session("New Chat")
    st.session_state.active_chat_id = new_chat_id
    st.session_state.history = []
    st.session_state.open_menu = None
    st.rerun()

st.sidebar.markdown("---")

# --- Fetch chats from DB (latest first) ---
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM chat_sessions ORDER BY created_at DESC")
chats = cursor.fetchall()
conn.close()

# --- Filter by search ---
if search_query.strip():
    chats = [c for c in chats if search_query.lower() in c[1].lower()]

# --- Keep open menu state ---
if "open_menu" not in st.session_state:
    st.session_state.open_menu = None

def open_chat(chat_id):
    """Load messages of the chosen chat."""
    st.session_state.active_chat_id = chat_id
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_message, ai_response FROM conversations WHERE chat_id=%s",
        (chat_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    st.session_state.history = []
    for u, a in rows:
        st.session_state.history.append({"role": "user", "parts": [u]})
        st.session_state.history.append({"role": "model", "parts": [a]})
    st.session_state.open_menu = None
    st.rerun()

# --- Style ---
st.markdown("""
<style>
.chat-row {display:flex;justify-content:space-between;
align-items:center;padding:6px 10px;margin-bottom:6px;
border-radius:6px;background:#262730;}
.chat-row:hover{background:#33343d;}
.chat-title{color:#fff;font-size:14px;font-weight:500;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:160px;}
.menu-btn{background:none;border:none;color:#aaa;font-size:18px;cursor:pointer;}
.menu-btn:hover{color:#fff;}
.option-btn{width:100%;text-align:left;padding:5px 12px;
background:none;border:none;color:#fff;font-size:13px;}
.option-btn:hover{background:#3a3b46;}
</style>
""", unsafe_allow_html=True)

# --- Display chats ---
if chats:
    for chat_id, title in chats:
        cols = st.sidebar.columns([5, 1])
        with cols[0]:
            if st.button(title, key=f"chat_{chat_id}", use_container_width=True):
                open_chat(chat_id)
        with cols[1]:
            if st.button("⋯", key=f"menu_{chat_id}", help="Options"):
                if st.session_state.open_menu == chat_id:
                    st.session_state.open_menu = None
                else:
                    st.session_state.open_menu = chat_id
                st.rerun()

        # --- Popup options ---
        if st.session_state.open_menu == chat_id:
            with st.sidebar:
                st.markdown(
                    f"<div style='background:#2d2e38;border-radius:6px;padding:4px 0;margin:-4px 0 6px 20px;'>",
                    unsafe_allow_html=True,
                )

                # Rename
                new_name = st.text_input("✏️ Rename", value=title, key=f"rename_{chat_id}")
                if st.button("💾 Save", key=f"save_{chat_id}"):
                    update_chat_title(chat_id, new_name)
                    st.success("Renamed ✅")
                    st.session_state.open_menu = None
                    st.rerun()

                # Export
                if st.button("⬇️ Export", key=f"export_{chat_id}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT user_message, ai_response FROM conversations WHERE chat_id=%s",
                        (chat_id,),
                    )
                    rows = cursor.fetchall()
                    conn.close()
                    buffer = io.StringIO()
                    for u, a in rows:
                        buffer.write(f"User: {u}\nAI: {a}\n\n")
                    st.download_button(
                        label="📁 Download",
                        data=buffer.getvalue(),
                        file_name=f"chat_{chat_id}.txt",
                        mime="text/plain",
                        key=f"download_{chat_id}",
                    )

                # Delete
                if st.button("🗑️ Delete", key=f"delete_{chat_id}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM chat_sessions WHERE id=%s", (chat_id,))
                    conn.commit()
                    conn.close()
                    st.warning("Deleted 🗑️")
                    st.session_state.open_menu = None
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.sidebar.info("No chats found.")


# =========================================================
# ---------------- Tabs ----------------
# =========================================================
tabs = st.tabs(["💬 Chat", "📄 RAG"])

# =========================================================
# ---------------- CHAT TAB ----------------
# =========================================================
with tabs[0]:
    st.markdown("### 💬 Conversation")

    # --- Chat Session Handling ---
    if "history" not in st.session_state:
        st.session_state.history = []
    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = None

    # --- Display chat messages (top to bottom) ---
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.history:
            role = msg["role"]
            with st.chat_message("user" if role == "user" else "assistant"):
                st.markdown(msg["parts"][0])

    # --- Chat input always rendered LAST ---
    user_input = st.chat_input("Type your message here...")

    if user_input:  #  Only proceed when user actually enters something
        # Add user message to session state first
        st.session_state.history.append({"role": "user", "parts": [user_input]})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        #  Create new chat session only for first message
        if st.session_state.active_chat_id is None:
            smart_title = generate_chat_title(user_input)
            chat_id = create_chat_session(smart_title)
            st.session_state.active_chat_id = chat_id

        # Generate AI reply
        with st.spinner("Thinking..."):
            ai_reply = get_ai_response(user_input, st.session_state.history)

        st.session_state.history.append({"role": "model", "parts": [ai_reply]})
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(ai_reply)

        # --- Save to database ---
        try:
            conn = get_connection()
            cursor = conn.cursor()
            if user_input and ai_reply and st.session_state.active_chat_id:
                cursor.execute(
                    "INSERT INTO conversations (user_message, ai_response, chat_id) VALUES (%s, %s, %s)",
                    (user_input, ai_reply, st.session_state.active_chat_id)
                )
                conn.commit()
            conn.close()
        except Exception as e:
            st.warning(f"⚠️ Database Error: {e}")

    st.caption("💬 Feel free to chat! Your conversation is saved automatically.")

# =========================================================
# ---------------- RAG TAB ----------------
# =========================================================
with tabs[1]:
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

    # Initialize RAG session states
    defaults = {
        "rag_ready": False, "rag_chunks": [], "rag_embeddings": None,
        "rag_index": None, "rag_history": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # --- File upload and index building ---
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")
        if st.button("📂 Build Index"):
            with st.spinner("Processing file..."):
                st.session_state.rag_chunks = chunk_text(text)
                idx, emb = build_index(st.session_state.rag_chunks)
                st.session_state.rag_index = idx
                st.session_state.rag_embeddings = emb
                st.session_state.rag_ready = True
                st.session_state.rag_history = []
                st.success(f"✅ Index built with {len(st.session_state.rag_chunks)} chunks")

    # --- Once RAG is ready ---
    if st.session_state.rag_ready:
        st.markdown("### 💬 Ask about your uploaded file")

        # Container for all chat messages
        rag_container = st.container()

        # --- Chat input stays BELOW conversation ---
        query = st.chat_input("Ask a question about the uploaded file...")

        if query:
            # Generate AI answer first
            with st.spinner("Retrieving relevant sections..."):
                results = search_similar(
                    query,
                    st.session_state.rag_chunks,
                    st.session_state.rag_embeddings,
                    st.session_state.rag_index,
                    top_k=3
                )
                context_text = "\n\n".join([c for c, _ in results])
                prompt = (
                    f"Answer only using the following context:\n{context_text}\n\n"
                    f"Question: {query}\n\n"
                    f"If the answer is not in the context, say: "
                    f"'Sorry, I cannot find that information in the provided file.'"
                )
                answer = get_ai_response(prompt)
                token_est = int(len(prompt) / 4)

            # ✅ Append full QA pair at once
            st.session_state.rag_history.append({
                "q": query,
                "a": answer,
                "sources": results,
                "tokens": token_est
            })

        # --- Display all conversation (after any new QA added) ---
        with rag_container:
            for msg in st.session_state.rag_history:
                with st.chat_message("user"):
                    st.markdown(msg["q"])
                with st.chat_message("assistant"):
                    st.markdown(msg["a"])
                    with st.expander("📌 Source Sections"):
                        for c, score in msg["sources"]:
                            st.markdown(f"**Relevance:** {round(score,3)}")
                            st.info(c)
                    st.caption(f"Approx tokens used: {msg['tokens']}")

        # --- Extra tools ---
        if st.session_state.rag_history:
            buffer = io.StringIO()
            for h in st.session_state.rag_history:
                buffer.write(f"Q: {h['q']}\nA: {h['a']}\n\n")
            st.download_button("⬇️ Export Chat History", buffer.getvalue(), "rag_history.txt")

        st.markdown("### 🔍 Search keyword in uploaded file")
        search_term = st.text_input("Enter keyword to search")
        if search_term:
            matches = [c for c in st.session_state.rag_chunks if search_term.lower() in c.lower()]
            if matches:
                st.write(f"Found {len(matches)} match(es):")
                for m in matches[:5]:
                    st.info(m)
            else:
                st.warning("No matches found.")

        if st.button("🔄 Replace File"):
            for k in ["rag_ready", "rag_chunks", "rag_embeddings", "rag_index", "rag_history"]:
                st.session_state[k] = defaults[k]
            st.rerun()
