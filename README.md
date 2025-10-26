AI Chat Application with RAG (Retrieval-Augmented Generation)
1. Model and Programming Language Used

AI Model: Google Gemini 2.0 Flash (via google-generativeai API)

Embeddings Model: Sentence Transformers (all-MiniLM-L6-v2)

Programming Language: Python 3.10 +

Frameworks / Libraries: Streamlit, MySQL (XAMPP), scikit-learn, sentence-transformers, python-dotenv

2. How to Run the Application

Step 1 – Environment Setup

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


Step 2 – Add Gemini API Key
Create a file named .env in the project folder and add:

GEMINI_API_KEY=your_gemini_api_key_here


Step 3 – Set Up MySQL Database

Start XAMPP → MySQL

Open phpMyAdmin

Create a database named ai_chat

Run:

CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT,
    ai_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


Step 4 – Run the App

streamlit run ui_app.py


Then open the link (usually http://localhost:8501
).

3. How the System Uses the Text File

The RAG tab enables document-based Q&A:

The user uploads a .txt file.

The system splits the text into overlapping chunks.

Each chunk is embedded using a transformer model.

When the user asks a question, the app finds the most similar chunks by cosine similarity.

Those chunks are passed to Gemini 2.0 Flash as context.

Gemini answers only using that content.

The interface displays:

The generated answer

Relevant text sections (highlighted)

Similarity / relevance scores

Options to search, export chat, and reload file

4. How to Use the Application
Chat Mode

Open Chat tab

Type a message and press Send

Gemini replies instantly

Each chat is saved in the MySQL database

RAG Mode

Open RAG tab

Upload a .txt file → click Build Index

Ask questions about the document

View answers, relevant sections, and similarity scores

Use search to locate keywords

Export chat history or replace file when needed

5. Screenshots (Working System)
Chat Interface

RAG Interface – Question 1

RAG Interface – Question 2

MySQL Database View (XAMPP)

6. Deliverables Checklist
Item	Status
Source Code (GitHub / ZIP)	✔️
Short README File	✔️
Working AI Chat + RAG Application	✔️
Screenshots of System	✔️
7. Developer Information

Name: R.D.D.S Rajamuni.
University: University of Jaffna – Faculty of Engineering
Project: AI Chat Application with RAG
Date: October 2025

8. Summary

This project demonstrates:

Integration of Google Gemini API with Streamlit UI

Implementation of a Retrieval-Augmented Generation pipeline

Real-time chat logging in MySQL

Optional features: highlighted context, similarity score, keyword search, export chat, replace file, and token usage display