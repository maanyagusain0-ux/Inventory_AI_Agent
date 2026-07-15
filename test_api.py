import requests

print("START")

response = requests.post(
    "http://127.0.0.1:11434/api/chat",
    json={
        "model": "llama3:latest",
        "messages": [
            {
                "role": "user",
                "content": "hello"
            }
        ],
        "stream": False
    },
    timeout=120
)

print("STATUS:", response.status_code)
print(response.json())