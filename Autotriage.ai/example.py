import sys
import os
from support_ai.pipeline import SupportPipeline
from support_ai.data_loader import TicketDataLoader
from colorama import init, Fore, Style

# Initialize colorama
init()

def print_analysis_result(result: dict, conversation: str):
    # Print chat preview
    print(f"\n{Fore.YELLOW}Chat Preview:{Style.RESET_ALL}")
    print(f"{conversation[:200]}...")
    
    print(f"\n{Fore.GREEN}AutoTriage.AI Analysis{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Let AI diagnose your support mess{Style.RESET_ALL}")
    print("-" * 40)
    
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL} {result['summary']}")
    print(f"\n{Fore.CYAN}Extracted Issue:{Style.RESET_ALL} {result['extracted_issue']}")
    print(f"\n{Fore.CYAN}Suggested Solution:{Style.RESET_ALL} {result['suggested_solution']}")
    
    # Color-code confidence score
    confidence = result['confidence_score']
    confidence_color = (
        Fore.GREEN if confidence > 0.8
        else Fore.YELLOW if confidence > 0.5
        else Fore.RED
    )
    print(f"\n{Fore.CYAN}Confidence Score:{Style.RESET_ALL} {confidence_color}{confidence:.2f}{Style.RESET_ALL}")

def main():
    try:
        # Load historical ticket data
        data_path = "[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Historical_ticket_data.csv"
        print(f"{Fore.BLUE}Loading data from:{Style.RESET_ALL} {data_path}")
        
        data_loader = TicketDataLoader(data_path)
        historical_data = data_loader.get_training_data()
        
        print(f"{Fore.BLUE}Initializing support pipeline...{Style.RESET_ALL}")
        pipeline = SupportPipeline()

        # Test conversations from our dataset
        test_conversations = [
            # Software Installation Failure case
            """
            Customer: "Hi there! I've been trying to install the latest update for your design software for hours. It keeps failing at 75% with an 'unknown error.' What's wrong?"
            Agent: "Hello! Thank you for reaching out. Let me help troubleshoot. Could you share a screenshot of the error message and confirm your operating system version?"
            Customer: "Sure, it's Windows 11. Here's the screenshot: [image link]. I've restarted twice, same issue."
            Agent: "Thank you for the details. This is a known conflict with third-party antivirus tools. Could you temporarily disable your antivirus and retry? I'll also send a direct download link as a workaround."
            Customer: "Oh, disabling the antivirus worked! Installation completed. Thanks for your help!"
            """,
            
            # Payment Gateway Integration case
            """
            Customer: "Hi, this is urgent! Your API is rejecting our payment gateway integration. Error: 'Invalid SSL certificate.' Our cert is valid and up-to-date!"
            Agent: "Hello! Let's investigate immediately. Could you share the output from openssl s_client -connect yourgateway.com:443?"
            Customer: "Here's the terminal output: [text]. See? No errors here."
            Agent: "Thank you! Our system requires TLS 1.3, but your server supports only up to TLS 1.2. Upgrading the protocol will resolve the authentication error."
            Customer: "Upgrading worked! Thanks for the quick fix!"
            """,
            
            # Account Synchronization case
            """
            Customer: "Hello! My project data isn't syncing between my laptop and tablet. Changes on one device don't show up on the other. Can you help?"
            Agent: "Hi there! Let's resolve this together. Are both devices logged into the same account? Could you share the sync logs?"
            Customer: "Yes, same account. Here's a log from my tablet: [file attached]."
            Agent: "Thanks for sharing! The log shows a corrupted sync token. I'll reset it manually. Go to Settings > Sync > Force Full Sync and wait 10 minutes. Let me know if it works!"
            Customer: "It's syncing now! Will this happen again?"
            """
        ]

        print(f"\n{Fore.BLUE}Processing {len(test_conversations)} test conversations...{Style.RESET_ALL}")
        
        for i, conversation in enumerate(test_conversations, 1):
            print(f"\n{'='*50}")
            print(f"{Fore.GREEN}Test Case {i}{Style.RESET_ALL}")
            print('='*50)
            
            result = pipeline.process(
                chat_text=conversation,
                ticket_data=historical_data
            )
            
            print_analysis_result(result, conversation)

    except FileNotFoundError as e:
        print(f"{Fore.RED}Error: Could not find the data file: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()


