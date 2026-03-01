import streamlit as st
import ollama
import chromadb
from sentence_transformers import SentenceTransformer
import random

# ---------------- CONFIG ----------------
LLM_MODEL = "phi3:mini"
EMBED_MODEL = "all-MiniLM-L6-v2"

# ---------------- LOAD EMBEDDING ----------------
@st.cache_resource
def load_embedder():
    return SentenceTransformer(EMBED_MODEL)

embedder = load_embedder()

# ---------------- INIT CHROMA ----------------
@st.cache_resource
def init_db():
    client = chromadb.Client()
    collection = client.get_or_create_collection("hire_ready")

    # Auto knowledge base
    if collection.count() == 0:
        documents = [
            # AMAZON
            ("Amazon", "HR", "Tell me about yourself. Rubric: structured answer, impact examples, leadership alignment."),
            ("Amazon", "Technical", "Explain time complexity of binary search. Rubric: Correct O(log n), divide and conquer explanation."),

            # TCS
            ("TCS", "HR", "Why should we hire you? Rubric: clarity, teamwork, company alignment."),
            ("TCS", "Technical", "Explain normalization in DBMS. Rubric: Explain 1NF, 2NF, 3NF clearly."),

            # INFOSYS
            ("Infosys", "HR", "Describe a challenging situation you faced. Rubric: problem solving, adaptability."),
            ("Infosys", "Technical", "Explain polymorphism in OOP. Rubric: compile-time and runtime explanation.")
        ]

        for i, (company, round_type, text) in enumerate(documents):
            collection.add(
                documents=[text],
                embeddings=[embedder.encode(text).tolist()],
                metadatas=[{
                    "company": company,
                    "round": round_type
                }],
                ids=[f"id_{i}"]
            )

    return collection

collection = init_db()

# ---------------- RETRIEVE QUESTION ----------------
def get_question(company, round_type):
    results = collection.query(
        query_embeddings=[embedder.encode(f"{company} {round_type}").tolist()],
        n_results=5,
        where={
            "$and": [
                {"company": company},
                {"round": round_type}
            ]
        }
    )

    questions = results["documents"][0]

    # Avoid crash if empty
    if not questions:
        return "No question found."

    return random.choice(questions)

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="HireReady Mock Interview")
st.title("🎯 HireReady – RAG Mock Interview Bot")

company = st.selectbox("Select Company", ["Amazon", "TCS", "Infosys"])
round_type = st.selectbox("Select Round", ["HR", "Technical"])

if "stage" not in st.session_state:
    st.session_state.stage = "question"
    st.session_state.count = 0
    st.session_state.feedback_list = []

MAX_QUESTIONS = 3

# ---------------- QUESTION STAGE ----------------
if st.session_state.stage == "question":

    if st.session_state.count >= MAX_QUESTIONS:
        st.session_state.stage = "scorecard"
        st.rerun()

    question = get_question(company, round_type)
    st.session_state.current_question = question

    st.subheader("🧑‍💼 Interviewer")
    st.write(question.split("Rubric:")[0])

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):
        if answer.strip() == "":
            st.warning("Please enter your answer.")
        else:
            st.session_state.answer = answer
            st.session_state.stage = "evaluation"
            st.rerun()

# ---------------- EVALUATION STAGE ----------------
elif st.session_state.stage == "evaluation":

    question = st.session_state.current_question

    # Extract rubric safely
    if "Rubric:" in question:
        rubric = question.split("Rubric:")[1]
    else:
        rubric = "Evaluate professionally."

    system_prompt = f"""
You are a strict professional interviewer.

Evaluate candidate answer strictly using this rubric:
{rubric}

Provide:
- Technical Accuracy (/10)
- Communication (/10)
- Confidence (/10)
- Culture Fit (/10)
- Short Feedback

Do NOT give hints.
Do NOT help the candidate.
Be professional and realistic.
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": st.session_state.answer}
        ]
    )

    feedback = response["message"]["content"]

    st.subheader("📊 Evaluation")
    st.write(feedback)

    st.session_state.feedback_list.append(feedback)
    st.session_state.count += 1

    if st.button("Next Question"):
        st.session_state.stage = "question"
        st.rerun()

# ---------------- FINAL SCORECARD ----------------
elif st.session_state.stage == "scorecard":

    st.header("🏆 Final Scorecard")

    summary_prompt = f"""
Based on these interview evaluations:

{st.session_state.feedback_list}

Generate a final structured scorecard including:
- Communication
- Technical Accuracy
- Confidence
- Culture Fit
- Overall Verdict
- Key Improvement Areas

Ground everything in previous feedback.
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": summary_prompt}]
    )

    st.write(response["message"]["content"])

    if st.button("Restart Interview"):
        st.session_state.clear()
        st.rerun()