from .base import BaseAgent
from typing import Dict, Any

class SummarizerAgent(BaseAgent):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        chat_text = input_data['chat_text']
        prompt = f"""Summarize this customer support conversation in 1-2 lines:\n\n{chat_text}"""
        summary = self.query_llm(prompt)
        return {"summary": summary.strip()}