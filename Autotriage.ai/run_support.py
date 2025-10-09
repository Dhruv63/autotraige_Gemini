from support_ai.pipeline import SupportPipeline
from support_ai.data_loader import TicketDataLoader

from colorama import init, Fore, Style
import json
import time

init()  # Initialize colorama

def format_output(result: dict) -> None:
    print(f"\n{Fore.CYAN}=== AutoTriage.AI Analysis ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Summary:{Style.RESET_ALL} {result['summary']}")
    print(f"{Fore.YELLOW}Issue:{Style.RESET_ALL} {result['extracted_issue']}")
    
    # Priority-based coloring
    priority_color = {
        "Critical": Fore.RED,
        "High": Fore.MAGENTA,
        "Medium": Fore.YELLOW,
        "Low": Fore.GREEN
    }
    print(f"{Fore.YELLOW}Priority:{Style.RESET_ALL} "
          f"{priority_color.get(result['priority_level'], '')}"
          f"{result['priority_level']}{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}Team:{Style.RESET_ALL} {result['assigned_team']}")
    print(f"{Fore.YELLOW}Estimated Time:{Style.RESET_ALL} {result['estimated_resolution_time']} hours")
    print(f"{Fore.YELLOW}Confidence:{Style.RESET_ALL} {result['confidence_score']:.2f}")
    
    print(f"\n{Fore.YELLOW}Suggested Solution:{Style.RESET_ALL}")
    print(result['suggested_solution'])
    
    print(f"\n{Fore.YELLOW}Action Items:{Style.RESET_ALL}")
    for item in result['action_items']:
        print(f"• {item}")

def process_support_ticket(conversation_text: str) -> dict:
    try:
        print(f"{Fore.CYAN}Processing support ticket...{Style.RESET_ALL}")
        
        # Show processing animation
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.5)
        print("\n")
        
        # Initialize components
        data_loader = TicketDataLoader("[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Historical_ticket_data.csv")
        historical_data = data_loader.get_training_data()
        pipeline = SupportPipeline()
        
        # Process the conversation
        result = pipeline.process(
            chat_text=conversation_text,
            ticket_data=historical_data
        )
        
        # Format and display results
        format_output(result)
        
        # Save analysis to file
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        with open(f"analysis_result_{timestamp}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return result
        
    except Exception as e:
        print(f"{Fore.RED}Error processing ticket: {str(e)}{Style.RESET_ALL}")
        raise

    # 3. Process the conversation
    result = pipeline.process(
        chat_text=conversation_text,
        ticket_data=historical_data
    )

    # 4. Print results
    print("\n=== AutoTriage.AI Analysis ===")
# Example usage

if __name__ == "__main__":
    # Example conversation
    conversation = """
    Customer: Hi there! I've been trying to install your software but it keeps failing at 75% with an unknown error.
    Agent: Hello! Could you share more details about the error message?
    Customer: It just says "Installation failed" and nothing else. I've tried three times already.
    """
    
    result = process_support_ticket(conversation)

# Example usage

if __name__ == "__main__":
    # Example conversation
    conversation = """
    Customer: Hi there! I've been trying to install your software but it keeps failing at 75% with an unknown error.
    Agent: Hello! Could you share more details about the error message?
    Customer: It just says "Installation failed" and nothing else. I've tried three times already.
    """
    
    result = process_support_ticket(conversation)



