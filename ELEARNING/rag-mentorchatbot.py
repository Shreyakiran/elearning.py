import streamlit as st
import ollama
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------- CONFIG ----------------
CHAT_MODEL = "phi3:mini"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# ---------------- DEFAULT RULES (No folder needed) ----------------
DEFAULT_RULES = [
    {
        "text": "Function names must use snake_case in Python.",
        "source": "Python Style Guide"
    },
    {
        "text": "Avoid using wildcard imports like 'from module import *'.",
        "source": "Import Guidelines"
    },
    {
        "text": "Variable names should be descriptive and not single letters unless in loops.",
        "source": "Naming Conventions"
    },
    {
        "text": "Line length should not exceed 100 characters.",
        "source": "Formatting Rules"
    },
    {
        "text": "Avoid deeply nested code blocks beyond 3 levels.",
        "source": "Code Readability Guide"
    }
]

# ---------------- LOAD EMBEDDING MODEL ----------------
@st.cache_resource
def load_embedder():
    return SentenceTransformer(EMBED_MODEL)

embedder = load_embedder()

documents = DEFAULT_RULES

# ---------------- SIMPLE RETRIEVAL ----------------
def retrieve_relevant_rules(code_input):
    doc_texts = [doc["text"] for doc in documents]

    doc_embeddings = embedder.encode(doc_texts)
    query_embedding = embedder.encode([code_input])[0]

    similarities = np.dot(doc_embeddings, query_embedding)

    top_indices = np.argsort(similarities)[-TOP_K:][::-1]

    return [documents[i] for i in top_indices]

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="CodeSensei")
st.title("🧠 CodeSensei - RAG Code Review Assistant")

language = st.selectbox("Select Programming Language", ["Python", "Java", "C++"])
code_input = st.text_area("Paste Your Code Here")

if st.button("Review Code"):

    if not code_input.strip():
        st.warning("Please paste code first.")
        st.stop()

    retrieved_rules = retrieve_relevant_rules(code_input)

    system_prompt = """
You are CodeSensei, a strict AI Code Review Mentor.

Your responsibilities:
- Review ONLY against provided rules.
- DO NOT check logic correctness.
- DO NOT invent rules.
- If no rule applies, say nothing.

Output format STRICTLY:

VERDICT: <Pass / Needs Improvement>

ISSUES:
1. <Issue>
   - Severity: <Low/Medium/High>
   - Violated Rule: "<Exact rule>"
   - Source: <Document Name>

POSITIVES:
- <Something good>
"""

    context_block = ""
    for i, rule in enumerate(retrieved_rules):
        context_block += f"""
[Rule {i+1}]
Source: {rule['source']}
Content:
{rule['text']}
"""

    user_prompt = f"""
Language: {language}

Submitted Code:
{code_input}

Retrieved Coding Standards:
{context_block}

Review strictly using the above rules.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = ollama.chat(model=CHAT_MODEL, messages=messages)

    st.subheader("📋 Code Review Result")
    st.markdown(response["message"]["content"])