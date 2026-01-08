from typing import Dict, Any
from .analyzer import TicketAnalyzer
import logging

class SupportPipeline:
    def __init__(self):
        self.analyzer = TicketAnalyzer()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def validate_input(self, chat_text: str, ticket_data: Dict[str, Any]) -> bool:
        if not chat_text or not isinstance(chat_text, str):
            self.logger.error("Invalid chat text provided")
            return False
        if not ticket_data or not isinstance(ticket_data, dict):
            self.logger.error("Invalid historical data provided")
            return False
        return True
    
    def process(self, chat_text: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Validate inputs
            if not self.validate_input(chat_text, ticket_data):
                raise ValueError("Invalid input data")

            # Analyze the ticket
            self.logger.info("Starting ticket analysis...")
            result = self.analyzer.analyze_ticket(chat_text, ticket_data)
            
            # Validate results
            if result.confidence < 0.3:
                self.logger.warning(f"Low confidence score: {result.confidence}")
            
            # Convert to dictionary format
            return {
                "summary": result.summary,
                "extracted_issue": result.issue,
                "suggested_solution": result.solution,
                "priority_level": result.priority,
                "assigned_team": result.team,
                "estimated_resolution_time": result.estimated_time,
                "confidence_score": result.confidence,
                "similar_cases": result.similar_cases,
                "action_items": result.action_items,
                "sentiment": result.sentiment
            }
        except Exception as e:
            self.logger.error(f"Error in pipeline: {str(e)}")
            raise

