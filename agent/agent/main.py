from models.voxtral import classify_query
from models.ollama import get_response_from_ollama

def handle_query(query):
    print(f"\n👉 User Query: {query}")

    intent, tags = classify_query(query)
    print(f"🧠 Intent: {intent} | Tags: {tags}")

    response = get_response_from_ollama(query, intent=intent, tags=tags)
    print(f"🤖 Response: {response}\n")

if __name__ == "__main__":
    user_query = input("💬 Enter your query: ")
    handle_query(user_query)
