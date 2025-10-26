import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel("gemini-2.0-flash")

def get_ai_response(prompt, history=[]):
    """
    Takes user input (prompt) + full chat history,
    returns model response as text.
    """
    try:
        # Create a chat session using the full conversation history
        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"[Error] {str(e)}"
