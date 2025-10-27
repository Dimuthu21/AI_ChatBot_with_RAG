import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel("gemini-2.0-flash")

def get_ai_response(prompt, history=[]):
    """Takes user input (prompt) + full chat history, returns model response as text."""
    try:
        if not prompt or not prompt.strip():
            return "[Error] Please enter a valid message."

        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"[Error] {str(e)}"

def generate_chat_title(prompt):
    """Use Gemini to suggest a short title for the chat topic."""
    try:
        if not prompt or not prompt.strip():
            return "New Chat"

        title_prompt = (
            f"Generate a short 3–5 word chat title describing this topic: '{prompt}'. "
            f"Return only the title, no punctuation or quotes."
        )
        response = model.generate_content(title_prompt)
        return response.text.strip() or "New Chat"
    except Exception:
        return "New Chat"
