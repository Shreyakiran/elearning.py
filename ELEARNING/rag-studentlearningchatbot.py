import streamlit as st
import ollama

CHAT_MODEL = "phi3:mini"

# ---------------- SESSION MEMORY INITIALIZATION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "preferences" not in st.session_state:
    st.session_state.preferences = {
        "subject": None,
        "difficulty": "medium",
        "weak_topics": []
    }

MAX_HISTORY = 10   # Manage context overflow

# ---------------- PAGE ----------------
st.set_page_config(page_title="Student Learning Memory Assistant")
st.title("🎓 Student Learning Memory Assistant")

# ---------------- SIDEBAR CONTROLS ----------------
with st.sidebar:
    st.header("📚 Learning Preferences")

    subject = st.selectbox(
        "Select Subject",
        ["Math", "Science", "Programming", "English", "Other"]
    )

    difficulty = st.selectbox(
        "Select Difficulty Level",
        ["easy", "medium", "hard"]
    )

    weak_topic = st.text_input("Add Weak Topic")

    if st.button("Save Preferences"):
        st.session_state.preferences["subject"] = subject
        st.session_state.preferences["difficulty"] = difficulty

        if weak_topic:
            st.session_state.preferences["weak_topics"].append(weak_topic)

        st.success("Preferences Saved ✅")

    if st.button("Reset Memory"):
        st.session_state.messages = []
        st.session_state.preferences = {
            "subject": None,
            "difficulty": "medium",
            "weak_topics": []
        }
        st.success("Memory Reset Successful 🔄")

# ---------------- DISPLAY CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
query = st.chat_input("Ask your study question...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    # ----------- BUILD CONTEXT -----------
    prefs = st.session_state.preferences

    system_prompt = f"""
You are a helpful learning assistant.

Student Preferences:
- Subject: {prefs['subject']}
- Difficulty Level: {prefs['difficulty']}
- Weak Topics: {prefs['weak_topics']}

Instructions:
- Adjust explanation complexity based on difficulty level.
- Give simpler explanation if difficulty = easy.
- Give detailed explanation if difficulty = hard.
- Focus more on weak topics if related.
- Keep answer clear and structured.
"""

    # Manage context overflow (keep last N messages)
    recent_history = st.session_state.messages[-MAX_HISTORY:]

    messages = [{"role": "system", "content": system_prompt}] + recent_history

    # ----------- MODEL RESPONSE -----------
    with st.chat_message("assistant"):
        response = ollama.chat(
            model=CHAT_MODEL,
            messages=messages,
            stream=True
        )

        full_response = ""

        for chunk in response:
            content = chunk["message"]["content"]
            full_response += content
            st.write(content)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })