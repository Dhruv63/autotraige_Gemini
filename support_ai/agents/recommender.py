from .base import BaseAgent
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.vectorizer = TfidfVectorizer()
        
    def find_similar_solution(self, current_issue: str, historical_data: Dict[str, List[str]]) -> Tuple[str, float]:
        # Combine historical issues with their context
        historical_contexts = [
            f"{issue} ({sentiment}, {priority})"
            for issue, sentiment, priority in zip(
                historical_data['issues'],
                historical_data['sentiments'],
                historical_data['priorities']
            )
        ]
        
        # Add current issue to the list for vectorization
        all_texts = historical_contexts + [current_issue]
        
        # Calculate TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarity scores
        similarities = cosine_similarity(
            tfidf_matrix[-1:],  # Current issue vector
            tfidf_matrix[:-1]   # Historical issues vectors
        )[0]
        
        # Find best match and round confidence score
        best_idx = np.argmax(similarities)
        confidence = round(float(similarities[best_idx]), 2)
        
        return historical_data['solutions'][best_idx], confidence

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        issue = input_data['extracted_issue']
        historical_data = input_data['ticket_data']
        
        solution, confidence = self.find_similar_solution(issue, historical_data)
        
        # Get top 3 similar cases
        similar_cases = [
            {
                "issue": historical_data['issues'][i],
                "solution": historical_data['solutions'][i],
                "sentiment": historical_data['sentiments'][i],
                "priority": historical_data['priorities'][i]
            }
            for i in range(min(3, len(historical_data['issues'])))
        ]
        
        return {
            "suggested_solution": solution,
            "confidence_score": confidence,
            "similar_cases": similar_cases
        }



