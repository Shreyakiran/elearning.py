# ---------------- IMPORTS ----------------
import os
import hashlib
import streamlit as st
import chromadb
import ollama
from pypdf import PdfReader
import requests

# ---------------- CONFIGURATION ----------------
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "docs"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "phi3:mini"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
N_RESULTS = 5
DIST_CUTOFF = 0.7

# ---------------- CHROMA INIT ----------------
@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

# ---------------- CHUNKING ----------------
def chunk_text(text: str):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - CHUNK_OVERLAP

    return chunks

# ---------------- READ FILE ----------------
def read_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
    return uploaded_file.read().decode("utf-8", errors="ignore")

# ---------------- EMBEDDING ----------------
def embed(texts):
    response = ollama.embed(model=EMBED_MODEL, input=texts)
    return response["embeddings"]

# ---------------- UNIQUE ID ----------------
def make_id(source, idx):
    return f"{hashlib.md5(source.encode()).hexdigest()}_{idx}"

# ---------------- INGEST ----------------
def ingest(uploaded_file, collection):
    name = uploaded_file.name
    text = read_file(uploaded_file)
    chunks = chunk_text(text)

    BATCH = 32

    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i+BATCH]

        collection.upsert(
            documents=batch,
            embeddings=embed(batch),
            metadatas=[{"source": name, "chunk": i+j}
                       for j in range(len(batch))],
            ids=[make_id(name, i+j)
                 for j in range(len(batch))]
        )

    return len(chunks)

# ---------------- RETRIEVE ----------------
def retrieve(query, collection):
    if collection.count() == 0:
        return []

    query_vec = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=min(N_RESULTS, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        if dist < DIST_CUTOFF:
            retrieved.append({
                "text": doc,
                "source": meta.get("source"),
                "distance": round(dist, 4)
            })

    return retrieved

# ---------------- BUILD PROMPT ----------------
def build_prompt(query, retrieved):
    if not retrieved:
        return f"Answer normally: {query}"

    context = "\n\n".join(
        f"[{c['source']}]\n{c['text']}"
        for c in retrieved
    )

    return f"""
Answer the question using ONLY the context below.
If answer is not in context say "I don't know."

CONTEXT:
{context}

QUESTION:
{query}
"""

# ---------------- STREAMLIT UI ----------------
st.set_page_config(
    page_title="RAG Chatbot",
    layout="centered"
)

st.title("📚 RAG Chatbot with Chroma + Ollama")

collection = get_collection()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📄 Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload txt or pdf files",
        type=["txt", "pdf"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Add Knowledge"):
        for file in uploaded_files:
            with st.spinner(f"Ingesting {file.name}..."):
                n = ingest(file, collection)
            st.success(f"{file.name} → {n} chunks added")

# ---------------- CHAT MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER QUERY ----------------
query = st.chat_input("Ask a question about your documents")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    retrieved_chunks = retrieve(query, collection)
    prompt = build_prompt(query, retrieved_chunks)

    with st.chat_message("assistant"):
        response = ollama.chat(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )

        answer = response["message"]["content"]
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })