import streamlit as st
from ollama import Client

client = Client(
    host="http://127.0.0.1:11434"
)

st.title("Ollama Test")

if st.button("Test Ollama"):

    st.write("STEP 1")

    response = client.chat(
        model="llama3:latest",
        messages=[
            {
                "role": "user",
                "content": "Hello"
            }
        ]
    )

    st.write("STEP 2")

    st.success(
        response["message"]["content"]
    )