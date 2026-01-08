from .base import BaseAgent
from typing import Dict, Any

class IssueExtractorAgent(BaseAgent):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        chat_text = input_data['chat_text']
        prompt = f"""Extract the main issue described in this conversation:\n\n{chat_text}\n\nIssue:"""
        issue = self.query_gemini(prompt)
        return {"extracted_issue": issue.strip()}