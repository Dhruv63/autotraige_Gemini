# Simple mock version of Voxtral
def classify_query(query):
    query = query.lower()
    if "printer" in query:
        return "hardware_issue", ["printer", "hardware"]
    elif "password" in query or "login" in query:
        return "account_issue", ["login", "password"]
    elif "internet" in query:
        return "connectivity_issue", ["internet", "network"]
    else:
        return "general_query", ["other"]
