import streamlit as st
import google.generativeai as genai
import time

# CONFIGURATION

api_key="AIzaSyDXXPSlY8Tt9CiTfayD6DP3rQMnkvF8Wk0"
MODEL="gemini-3-flash-preview"
SYSTEM_PROMPT = "You are a helpful chatbot."


genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name=MODEL,
    system_instruction=SYSTEM_PROMPT
)


# SESSION STATE SETUP


if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot_name" not in st.session_state:
    st.session_state.bot_name = "dinku"


# PAGE SETTINGS


st.set_page_config(
    page_title="First Chatbot",
    page_icon="🙂",
    layout="centered"
)

# Sidebar
with st.sidebar:
    st.title("Chatbot Settings")
    st.session_state.bot_name = st.text_input(
        "Bot Name",
        value=st.session_state.bot_name
    )

# Main Title
st.header(f"Welcome to {st.session_state.bot_name} 🤖")
st.divider()


# DISPLAY OLD MESSAGES


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# USER INPUT


user_input = st.chat_input("Type your message...")

if user_input:
    # Store & Show User Message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": time.strftime("%H:%M:%S")
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Typing..."):
            response = st.session_state.chat.send_message(user_input)
            reply = response.text
            st.markdown(reply)

    # Store Assistant Reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "timestamp": time.strftime("%H:%M:%S")
    })