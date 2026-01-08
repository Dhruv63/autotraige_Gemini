import json
import time
from dotenv import load_dotenv

load_dotenv()
from typing import Dict, Any

from colorama import init, Fore, Style

from support_ai.pipeline import SupportPipeline
from support_ai.data_loader import TicketDataLoader

# Initialize colorama for terminal output
init()

def process_support_ticket(conversation_text: str) -> Dict[str, Any]:
    """
    Analyzes a support ticket conversation and returns the analysis results.
    This is the main entry point for the backend pipeline.
    """
    try:
        # 1. Initialize the data loader with historical data
        data_loader = TicketDataLoader(
            "[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Historical_ticket_data.csv"
        )
        historical_data = data_loader.get_training_data()

        # 2. Create a pipeline instance
        pipeline = SupportPipeline()

        # 3. Process the conversation
        print(f"{Fore.CYAN}Processing support ticket...{Style.RESET_ALL}")
        result = pipeline.process(
            chat_text=conversation_text,
            ticket_data=historical_data
        )
        print(f"{Fore.GREEN}Analysis complete.{Style.RESET_ALL}")

        # 4. Save the analysis to a JSON file (optional, but good practice)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_filename = f"analysis_result_{timestamp}.json"
        with open(output_filename, "w") as f:
            # Convert numpy types to native Python types for JSON serialization
            serializable_result = json.loads(json.dumps(result, default=lambda o: o.__dict__))
            json.dump(serializable_result, f, indent=4)
        print(f"Results saved to {output_filename}")


        return result

    except Exception as e:
        print(f"{Fore.RED}Error processing ticket: {str(e)}{Style.RESET_ALL}")
        # Return a dictionary with the error message
        return {"error": str(e)}


def format_and_print_output(result: dict) -> None:
    """Formats and prints the analysis result to the console."""
    print(f"\n{Fore.CYAN}=== AutoTriage.AI Analysis ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Summary:{Style.RESET_ALL} {result.get('summary', 'N/A')}")
    print(f"{Fore.YELLOW}Issue:{Style.RESET_ALL} {result.get('extracted_issue', 'N/A')}")

    priority_color = {
        "Critical": Fore.RED, "High": Fore.MAGENTA,
        "Medium": Fore.YELLOW, "Low": Fore.GREEN
    }
    priority = result.get('priority_level', 'N/A')
    print(f"{Fore.YELLOW}Priority:{Style.RESET_ALL} {priority_color.get(priority, '')}{priority}{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}Team:{Style.RESET_ALL} {result.get('assigned_team', 'N/A')}")
    print(f"{Fore.YELLOW}Confidence:{Style.RESET_ALL} {result.get('confidence_score', 0.0):.2f}")

    print(f"\n{Fore.YELLOW}Suggested Solution:{Style.RESET_ALL}")
    print(result.get('suggested_solution', 'No solution generated.'))

    print(f"\n{Fore.YELLOW}Action Items:{Style.RESET_ALL}")
    for item in result.get('action_items', []):
        print(f"• {item}")


# This block allows the script to be run directly from the command line for testing
if __name__ == "__main__":
    example_conversation = """
    Customer: \"Hello, my smart thermostat keeps disconnecting from the Wi-Fi every few hours. I have to manually reconnect it.\"
    Agent: \"Hello! I can help. What is the model of your thermostat and your Wi-Fi router?\"
    Customer: \"It's the 'ClimateControl 3000' and my router is a 'NetSphere AX'.\"
    Agent: \"Thank you. The NetSphere AX router has a 'band-steering' feature that can cause issues. Please log into your router's settings and give the 2.4GHz and 5GHz networks separate names, then connect the thermostat to the 2.4GHz network.\"
    Customer: \"Okay, I've done that. It seems stable now. Thanks!\"
    """
    analysis_result = process_support_ticket(example_conversation)
    if "error" not in analysis_result:
        format_and_print_output(analysis_result)