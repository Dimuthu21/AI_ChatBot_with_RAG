# ⚛  Ragnova (AI Chat Application with RAG)

## 🧠 Overview
This project demonstrates the integration of **Google Gemini 2.0 Flash** with a **Retrieval-Augmented Generation (RAG)** pipeline using **Streamlit** and **MySQL (XAMPP)**.  
It enables real-time chat, document-based Q&A, and keyword-based search — all through a modern and interactive UI.

---

## 🧩 Technologies Used

| Component | Description |
|------------|-------------|
| **AI Model** | Google Gemini 2.0 Flash (via `google-generativeai` API) |
| **Embeddings Model** | Sentence Transformers – `all-MiniLM-L6-v2` |
| **Programming Language** | Python 3.10+ |
| **Frameworks / Libraries** | Streamlit, scikit-learn, sentence-transformers, python-dotenv |
| **Database** | MySQL (XAMPP) |

---

## ⚙️ Setup and Installation

### Step 1 – Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # On Windows
# or
source venv/bin/activate     # On macOS/Linux
Install dependencies:

pip install -r requirements.txt

Step 2 – Add Gemini API Key

Create a file named .env in the root project folder and include:

GEMINI_API_KEY=your_gemini_api_key_here

Step 3 – Set Up MySQL Database

Start XAMPP → Launch MySQL

Open phpMyAdmin

Create a database named ai_chat

Run this SQL command:

CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT,
    ai_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Step 4 – Run the Application
streamlit run ui_app.py


Then open http://localhost:8501
 in your browser.

💬 Application Modes
🗨️ Chat Mode

Open the Chat tab

Type a message → click Send

Gemini 2.0 Flash replies instantly

Every chat session is saved in the MySQL database

📄 RAG Mode

Open the RAG tab

Upload a .txt file and click Start Conversation

Ask questions directly from the document

The system retrieves the most relevant text chunks using cosine similarity

Gemini generates context-aware answers

You can view:

Highlighted relevant sections

Similarity scores

Keyword search results

Options to Export Chat or Reload File

🔍 How RAG Works

The uploaded .txt file is split into overlapping text chunks

Each chunk is embedded using the Sentence Transformer model

When a question is asked:

The system finds top-matching chunks using cosine similarity

These chunks are passed as context to Gemini 2.0 Flash

Gemini generates a response using only that relevant content

Results are displayed with highlighted context and relevance indicators

📸 Screenshots
Chat Interface

RAG Interface – Question 1

RAG Interface – Question 2

💡 Ensure that your screenshots are located in a folder named ss inside the main project directory.

project_folder/
│
├── ui_app.py
├── rag_engine.py
├── chat_logic.py
├── db_config.py
├── ss/
│   ├── chat_interface.png
│   ├── rag_interface_1.png
│   ├── rag_interface_2.png

✅ Deliverables Checklist
Item	Status
Source Code (GitHub / ZIP)	✔️
Short README File	✔️
Working AI Chat + RAG App	✔️
Screenshots Included	✔️
👨‍💻 Developer Information

Name: Dimuthu Shalinda
University: University of Jaffna – Faculty of Engineering
Project: AI Chat Application with RAG
Date: October 2025

🏁 Summary

This project highlights:

Real-time chat integration with Google Gemini 2.0 Flash

A complete Retrieval-Augmented Generation (RAG) workflow

Persistent chat logging through MySQL

Advanced functionality including:

Highlighted context visualization

Similarity scoring

Keyword-based search

Chat export and file reload options

This system demonstrates the potential of combining LLM reasoning with retrieval-based document grounding, serving as a foundation for intelligent, data-driven applications.