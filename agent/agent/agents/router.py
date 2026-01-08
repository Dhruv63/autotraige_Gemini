# Future logic for routing to specialized agents
def route_task(intent, query):
    if intent == "hardware_issue":
        return "hardware_agent"
    elif intent == "account_issue":
        return "auth_agent"
    else:
        return "default_agent"
