from run_support import process_support_ticket

def process_conversation_file(file_path: str):
    # Read the conversation from the file
    with open(file_path, 'r', encoding='utf-8') as f:
        conversation_text = f.read()
    
    # Process the conversation using our support pipeline
    result = process_support_ticket(conversation_text)
    return result

# Test with a specific conversation file
if __name__ == "__main__":
    result = process_conversation_file("[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Conversation/Software Installation Failure.txt")
    
    print("\n=== Support Ticket Analysis ===")
    print(f"Summary: {result['summary']}")
    print(f"Extracted Issue: {result['extracted_issue']}")
    print(f"Suggested Solution: {result['suggested_solution']}")
    print(f"Confidence Score: {result['confidence_score']:.2f}")


