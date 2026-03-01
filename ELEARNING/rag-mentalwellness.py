import streamlit as st
import ollama
from datetime import datetime
import pandas as pd

CHAT_MODEL = "phi3:mini"
MAX_HISTORY = 8

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Mental Wellness Support System",
    page_icon="🧠",
    layout="wide"
)

# ---------------- DARK MODE TOGGLE ----------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.header("⚙ Settings")
    st.session_state.dark_mode = st.toggle("🌙 Dark Mode")

# ---------------- THEME STYLE ----------------
if st.session_state.dark_mode:
    background = "#1e1e1e"
    text_color = "white"
else:
    background = "#f4f8f7"
    text_color = "black"

st.markdown(f"""
<style>
.main {{
    background-color: {background};
    color: {text_color};
}}

.stChatMessage {{
    border-radius: 15px;
    padding: 10px;
}}

div[data-testid="stSidebar"] {{
    background-color: #e6f2f1;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🧠 Mental Wellness Support System")
st.markdown("### 💛 Supportive • Safe • Educational")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ---------------- RISK KEYWORDS ----------------
HIGH_RISK = ["suicide", "kill myself", "end my life", "self harm"]
MODERATE_RISK = ["depressed", "hopeless", "anxious", "lonely"]

# ---------------- RISK DETECTION ----------------
def detect_risk(text):
    text = text.lower()
    for word in HIGH_RISK:
        if word in text:
            return "high", 3
    for word in MODERATE_RISK:
        if word in text:
            return "moderate", 2
    return "low", 1

# ---------------- SUPPORT RESPONSE ----------------
def generate_response(user_input):
    prompt = f"""
You are a supportive mental wellness assistant.
Provide emotional support only.
Do not give therapy or medical advice.

User: {user_input}
"""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": prompt}]
    )

    return response["message"]["content"]

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
query = st.chat_input("💛 I'm here to listen. What's on your mind?")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    risk_level, mood_score = detect_risk(query)

    # Log mood
    st.session_state.mood_log.append({
        "time": datetime.now(),
        "score": mood_score
    })

    with st.chat_message("assistant"):

        if risk_level == "high":
            st.error("⚠ High Risk Detected")
            response_text = """
I'm really sorry you're feeling this way.

If you're in immediate danger, please contact emergency services.

📞 India Helpline: 1800-599-0019

You deserve support.
"""
            st.markdown(response_text)

        else:
            if risk_level == "moderate":
                st.warning("💛 It sounds like you're having a tough time.")

            response_text = generate_response(query)
            st.markdown(response_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })

# ---------------- EMOTION METER ----------------
st.markdown("---")
st.subheader("📊 Emotion Meter")

if st.session_state.mood_log:
    latest_score = st.session_state.mood_log[-1]["score"]

    if latest_score == 1:
        st.success("Current Emotional State: Stable 😊")
    elif latest_score == 2:
        st.warning("Current Emotional State: Moderate Distress 💛")
    else:
        st.error("Current Emotional State: High Risk ⚠")

# ---------------- MOOD TRACKING CHART ----------------
st.markdown("---")
st.subheader("📈 Mood Tracking Chart")

if st.session_state.mood_log:
    df = pd.DataFrame(st.session_state.mood_log)
    st.line_chart(df["score"])

# ---------------- ADMIN MONITORING ----------------
st.markdown("---")
st.subheader("🔐 Admin Monitoring Panel")

admin_password = st.text_input("Enter Admin Password", type="password")

if admin_password == "admin123":
    st.success("Admin Access Granted")
    st.write("Total Conversations:", len(st.session_state.messages))
    st.write("Total Mood Entries:", len(st.session_state.mood_log))
    st.dataframe(pd.DataFrame(st.session_state.mood_log))
elif admin_password:
    st.error("Incorrect Password")

# ---------------- ACADEMIC FOOTER ----------------
st.markdown("---")
st.caption("🎓 Academic Project: AI-based Mental Wellness Support System with Risk Detection, Mood Tracking, and Safety Escalation Mechanism.")