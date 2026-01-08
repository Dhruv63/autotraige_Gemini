from flask import Flask, request, jsonify
from flask_cors import CORS
from support_ai.pipeline import SupportPipeline
from support_ai.data_loader import TicketDataLoader
from support_ai.email_service import EmailService
from datetime import datetime
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

RESULTS_DIR = "ticket_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Global variable to hold the pipeline and a startup error message
pipeline = None
startup_error = None

try:
    data_loader = TicketDataLoader("[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Historical_ticket_data.csv")
    historical_data = data_loader.get_training_data()
    if not historical_data.get('issues'):
        raise FileNotFoundError("Historical data is empty. Check the CSV file and path.")
    pipeline = SupportPipeline()
    logging.info("Pipeline and historical data loaded successfully.")
except Exception as e:
    logging.error(f"FATAL: Could not initialize backend pipeline. Error: {e}")
    startup_error = str(e)


@app.route('/chat', methods=['POST'])
def chat():
    if not pipeline:
        error_message = "Backend pipeline is not available. "
        if startup_error:
            error_message += f"Reason: {startup_error}"
        else:
            error_message += "An unknown error occurred during initialization."
        return jsonify({"error": error_message}), 500

    conversation_list = request.get_json().get('conversation_history', [])
    conversation_text = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in conversation_list])
    try:
        agent_reply = pipeline.analyzer.generate_solution(conversation_text)
        return jsonify({"agent_reply": agent_reply})
    except Exception as e:
        logging.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": f"Failed to generate response: {e}"}), 500

@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    if not pipeline:
        error_message = "Backend pipeline is not available. "
        if startup_error:
            error_message += f"Reason: {startup_error}"
        else:
            error_message += "An unknown error occurred during initialization."
        return jsonify({"error": error_message}), 500

    conversation_list = request.get_json().get('conversation_history', [])
    conversation_text = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in conversation_list])
    try:
        # Use pipeline.process to satisfy correct key mapping (extracted_issue, priority_level, etc.)
        final_analysis = pipeline.process(conversation_text, historical_data)

        ticket_id = f"TICKET_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        final_analysis['ticket_id'] = ticket_id
        final_analysis['conversation_history'] = conversation_list
        
        # Check for Critical Priority and Alert Boss
        if final_analysis.get('priority_level') == 'Critical':
            try:
                email_service = EmailService()
                email_service.send_critical_alert(final_analysis)
            except Exception as e:
                logging.error(f"Could not send email alert: {e}") # Don't fail the ticket submission

        file_path = os.path.join(RESULTS_DIR, f'{ticket_id}.json')
        with open(file_path, 'w') as f:
            json.dump(final_analysis, f, indent=4)

        logging.info(f"Ticket submitted and saved to {file_path}")
        return jsonify({"message": "Ticket submitted successfully", "ticket_id": ticket_id}), 200
    except Exception as e:
        logging.error(f"Error submitting ticket: {e}")
        return jsonify({"error": f"Failed to submit ticket: {e}"}), 500

if __name__ == '__main__':
    # Add a check here to prevent running a broken app
    if not pipeline:
        print("="*80)
        print("FATAL: AutoTriage.AI backend could not start.")
        print(f"ERROR: {startup_error}")
        print("Please check the logs and resolve the issue before running again.")
        print("Common issues include:")
        print("  - Missing or incorrect path to 'Historical_ticket_data.csv'")
        print("  - Errors within the pandas library reading the CSV")
        print("  - Problems with the 'ollama' AI model service.")
        print("="*80)
    else:
        app.run(host='0.0.0.0', port=5000)