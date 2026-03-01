import google.generativeai as genai

api_key="AIzaSyBlc5y2R-P-sI9nDCj95AD8yYPXUb10Rvg"
MODEL="gemini-3-flash-preview"
SYSTEM_PROMPT = "You are a helpful chatbot."

def setup():
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT
    )
    chat = model.start_chat(history=[])
    return chat

def ask_ai_stream(chat, message: str) -> str:
    response = chat.send_message(message, stream=True)
    full_reply = ""

    for chunk in response:
        print(chunk.text, end="", flush=True)
        full_reply += chunk.text

    print("\n")
    return full_reply


chat = setup()

while True:
    user_input = input("you: ").strip()
    ask_ai_stream(chat, user_input)