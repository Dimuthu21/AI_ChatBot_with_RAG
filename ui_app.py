import streamlit as st
from chat_logic import get_ai_response
from db_config import get_connection
from rag_engine import chunk_text, build_index, search_similar
import io
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="AI Chat App", page_icon="🤖", layout="centered")
st.title("🤖 AI Chat Application")
st.caption("Powered by Google Gemini 2.0 Flash + MySQL (XAMPP) + RAG System")

# ---------------- Tabs ----------------
tabs = st.tabs(["💬 Chat", "📄 RAG"])

# ---------------- CHAT TAB ----------------
with tabs[0]:
    st.markdown("### 💬 Conversation")

    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []

    # --- Display chat messages (top to bottom) ---
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.history:
            role = msg["role"]
            with st.chat_message("user" if role == "user" else "assistant"):
                st.markdown(msg["parts"][0])

    # --- Chat input always rendered LAST ---
    # (kept outside the container so it stays at bottom)
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to session state first
        st.session_state.history.append({"role": "user", "parts": [user_input]})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

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
            cursor.execute(
                "INSERT INTO conversations (user_message, ai_response) VALUES (%s, %s)",
                (user_input, ai_reply)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            st.warning(f"⚠️ Database Error: {e}")

    st.caption("💬 Continuous chat enabled | Input box stays below conversation")

# ---------------- RAG TAB ----------------
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
