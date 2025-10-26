from chat_logic import get_ai_response
import mysql.connector
from db_config import get_connection

def main():
    print(" AI Chat Application Started (type 'exit' to quit)\n")

    history = []  

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chat ended.")
            break

        ai_response = get_ai_response(user_input, history)
        print(f"AI: {ai_response}\n")

        # Add to memory
        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [ai_response]})

        # Save to DB
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (user_message, ai_response) VALUES (%s, %s)",
                (user_input, ai_response)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB Error] {e}")

if __name__ == "__main__":
    main()
