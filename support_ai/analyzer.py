from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import os
import google.generativeai as genai
import logging
import warnings

# Suppress the "google.generativeai" deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)

@dataclass
class AnalysisResult:
    summary: str = "N/A"
    issue: str = "N/A"
    solution: str = "N/A"
    priority: str = "Medium"
    team: str = "Technical"
    estimated_time: float = 2.0
    confidence: float = 0.0
    similar_cases: List[Dict] = None
    action_items: List[str] = None
    sentiment: str = "Neutral"

class TicketAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def query_llm(self, prompt: str) -> str:
        try:
            if "GEMINI_API_KEY" not in os.environ:
                logging.error("GEMINI_API_KEY not found.")
                return "Error: GEMINI_API_KEY not set."
            
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemma-3-4b-it')
            logging.info(f"Querying model 'gemma-3-4b-it'...")
            
            response = model.generate_content(prompt)
            logging.info("Successfully received response from model.")
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error in query_llm: {e}")
            return "Could not generate a response due to a backend error."

    def generate_solution(self, conversation_text: str) -> str:
        prompt = f"""
You are a detailed-oriented Support Agent.
- **Goal**: Resolve the user's technical issue efficiently.
- **Context**: A chat history is provided below.
- **Instruction**: Read the ENTIRE conversation history. Do NOT repeat questions that have already been asked or answered. Use the history to build a complete picture of the problem.
- **Special Rule**: If the user says they are "submitting a ticket", "creating a ticket", or implies they are done and want to submit, your ONLY response must be: "Yes, sure." Do not offer further help in that case.
- **Response**: Provide the next logical step, solution, or question. Be helpful, concise, and do not repeat yourself.

Conversation History:
---
{conversation_text}
---
Your Response:
        """
        return self.query_llm(prompt)

    def generate_summary(self, conversation: str) -> str:
        prompt = f"""Summarize this support chat in one sentence:

{conversation}"""
        return self.query_llm(prompt)
    def derive_technical_solution(self, conversation: str) -> str:
        prompt = f"""Review the technical support conversation below.
Extract and summarize the technical solution that was proposed or the recommended next steps to fix the issue.
Do NOT reply as a chat agent. Just state the solution clearly.

Conversation:
{conversation}"""
        return self.query_llm(prompt)

    def extract_issue(self, conversation: str) -> str:
        prompt = f"""What is the single main technical problem related to the software product in this chat? Be specific and brief.

{conversation}"""
        return self.query_llm(prompt)

    def determine_priority(self, issue: str, sentiment: str) -> str:
        issue_lower = issue.lower()
        if sentiment in ['urgent', 'negative']: return 'High'
        if any(word in issue_lower for word in ['critical', 'down', 'error']): return 'Critical'
        if any(word in issue_lower for word in ['problem', 'failing', "won't open"]): return 'High'
        return 'Medium'

    def determine_team(self, issue: str) -> str:
        issue_lower = issue.lower()
        routing_rules = {
            'Technical': ['installation', 'error', 'bug', 'crash', 'technical', 'router', 'word', 'software', 'closing'],
            'Billing': ['payment', 'charge', 'invoice'],
            'Security': ['password', 'access', 'authentication'],
        }
        for team, keywords in routing_rules.items():
            if any(keyword in issue_lower for keyword in keywords): return team
        return 'Technical'

    def calculate_similarity(self, text1: Any, text2: Any) -> float:
        try:
            text1, text2 = str(text1).lower().strip(), str(text2).lower().strip()
            if not text1 or not text2: return 0.0
            vectors = self.vectorizer.fit_transform([text1, text2])
            return round(cosine_similarity(vectors[0:1], vectors[1:2])[0][0], 2)
        except: return 0.0

    def find_similar_cases(self, issue: str, historical_data: Dict) -> List[Dict]:
        if not historical_data or not historical_data.get('issues'): return []
        self.vectorizer = TfidfVectorizer() # Re-initialize for fresh vocabulary
        
        all_issues = historical_data['issues'] + [issue]
        tfidf_matrix = self.vectorizer.fit_transform(all_issues)
        
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
        
        top_indices = similarities.argsort()[-3:][::-1]
        
        similar_cases = []
        for i in top_indices:
            if similarities[i] > 0.1:
                similar_cases.append({
                    "issue": historical_data['issues'][i],
                    "solution": historical_data['solutions'][i],
                    "similarity": float(similarities[i])
                })
        return similar_cases

    def analyze_sentiment(self, conversation: str) -> str:
        prompt = f"""Analyze the sentiment of the last customer message in this chat and respond with one word (Positive/Negative/Neutral):

{conversation}"""
        return self.query_llm(prompt)

    def calculate_confidence(self, similar_cases: List[Dict]) -> float:
        if not similar_cases: return 0.1 # Return a low base score if no matches
        best_similarity = max(case['similarity'] for case in similar_cases)
        confidence = 0.25 + (best_similarity * 0.7)
        return round(min(confidence, 0.95), 2)

    def analyze_ticket(self, conversation: str, historical_data: Dict) -> AnalysisResult:
        issue = self.extract_issue(conversation)
        sentiment = self.analyze_sentiment(conversation)
        priority = self.determine_priority(issue, sentiment)
        team = self.determine_team(issue)
        similar_cases = self.find_similar_cases(issue, historical_data)
        confidence = self.calculate_confidence(similar_cases)
        summary = self.generate_summary(conversation)
        solution = self.derive_technical_solution(conversation) # Use dedicated solution extractor
        
        return AnalysisResult(
            summary=summary, issue=issue, solution=solution, priority=priority,
            team=team, confidence=confidence, similar_cases=similar_cases, sentiment=sentiment
        )