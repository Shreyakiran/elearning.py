import streamlit as st
import time

st.set_page_config(
    page_title="First Chatbot",
    page_icon=":)",
    layout="centered"
)

st.session_state.messages = []
st.session_state.bot_name ="sinchuu"

with st.sidebar:
    st.title("Chatbot Settings")
    st.session_state.bot_name = st.text_input(
        "Bot Name", value=st.session_state.bot_name
        )

st.header("Welcome")
st.divider()


#Conversation Session
for msg in st.session_state.messages:
    role = msg['role']
    content = msg['content']
    with st.chat_message(role):
        st.markdown(content)


user_input = st.text_input("Your prompt to chatbot")
if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": time.strftime("%H:%M:%S")
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Typing..."):
            time.sleep(0.8)
        response = "Hello"
        st.markdown(response)