from ollama import Client

print("STEP 1")

client = Client(
    host="http://127.0.0.1:11434"
)

print("STEP 2")

response = client.chat(
    model="llama3:latest",
    messages=[
        {
            "role": "user",
            "content": "Hello"
        }
    ]
)

print("STEP 3")

print(response["message"]["content"])