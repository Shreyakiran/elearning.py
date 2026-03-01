import streamlit as st
import ollama

# PAGE CONFIG (MUST BE FIRST)

st.set_page_config(
    page_title="Ollama Chatbot",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = "You are a helpful chatbot."



if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot_name" not in st.session_state:
    st.session_state.bot_name = "sinchuu"



with st.sidebar:
    st.title("Chatbot Settings")

    st.session_state.bot_name = st.text_input(
        "Bot Name",
        value=st.session_state.bot_name
    )

    if st.button("Clear Chat"):
        st.session_state.messages = []



st.header(f"Welcome to {st.session_state.bot_name} 🤖")
st.divider()

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])



user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response from Ollama
    with st.chat_message("assistant"):
        with st.spinner("Typing..."):
            try:
                response = ollama.chat(
                    model="phi3:mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state.messages
                    ]
                )

                reply = response["message"]["content"]

            except Exception as e:
                reply = f"Error: {e}"

            st.markdown(reply)

    # Add assistant reply to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })