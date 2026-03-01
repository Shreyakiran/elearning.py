#import phase
import os
from google import genai
from google.genai import types
import streamlit as st
import requests
import json

TOOLS = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="search_books",
        description=("Search the open library database for the books and title,author, or subject matching the query,"
            "Returns the book titles,authors, and publication years etc"),
        parameters={
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":"The search query for books, can be title,author or subject"
                },
                "search_type":{
                    "type":"string",
                    "enum":["general","title","author","subject"],
                    "description":"The type of search to perform, can be general, title, author "
                
            },
            },
            "required":["query"]
        }
    )])



tools=[
    {
        "type":"",
        "function":{
            "name":"search_books",
            "description":"Search the open library database for the books and title,author, or subject matching the query,"
            "Returns the book titles,authors, and publication years etc",
        },
        "parameters":{
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":""

            },
            "required":["query"]

            
        }
    }
    }]
def search_books( query,search_type):
    base="https://openlibrary.org/search.json?q=novels"
    params ={
        "limit":6,
        "fields":"key,title,author_name,cover_i,edition_count,subject"
    }

    if search_type == "title":
        params["title"]=query
    elif search_type == "author":
        params["author"]=query

    try:
        resp = requests.get(base,params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    
        books=[]
        for doc in data.get("docs",[]):
            books.append({
                "key":doc.get("key"),
                "title":doc.get("title"),
                "author":doc.get("author_name",["Unknown"])[0],
                "cover_id":doc.get("cover_i"),
                

            })
        return {"total_found":len(books),"books":books}
    except(Exception):
        print(Exception)

st.set_page_config(
    page_title="Rag chatbot",
    page_icon="",
    layout="centered"
)  

api_key = "AIzaSyBJQq2ht_DMrYCB0nf_6vrbtRvFUuk1thg"
MODEL = "gemini-3-flash-preview"



prompt = st.text_input("Ask about books",placeholder="crime thrillers books")
if st.button("Ask") and prompt:
    client = genai.Client(api_key=api_key)
    with st.status("Asking LLM for tool call analysis"):
        response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        
       config=types.GenerateContentConfig(
           system_instruction="you are a book discovery assistant use available tools to find books for users",
           tools=[TOOLS]
    )
)
    print(f"Response from gemini{response}")
    candidate = response.candidates[0]
    parts =candidate.content.parts[0]
    st.text(f"{parts.function_call}")
    st.text(f"{parts.function_call.args.get('query')}")
    query = parts.function_call.args.get("query")
    if parts.function_call.name == "search_books":
        result = search_books(query, "title")
        st.caption(result)

        output = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        
        config=types.GenerateContentConfig(
            system_instruction=(f"use the above recommendations and craft it "
                                f"beautifully to user {result}"),
        )
    )


    candidate = output.candidates[0]
    parts = candidate.content.parts[0]
    st.markdown(f"{parts.text}")