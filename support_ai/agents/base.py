from abc import ABC, abstractmethod
import google.generativeai as genai
import warnings

# Suppress the "google.generativeai" deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
import os
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self):
        if "GEMINI_API_KEY" not in os.environ:
            # Fallback or warning could be added here, but raising helps debug
            pass 
        else:
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemma-3-4b-it')

    def query_gemini(self, prompt: str) -> str:
        try:
            if not hasattr(self, 'model'):
                # Try to init again if somehow skipped or for safety
                if "GEMINI_API_KEY" in os.environ:
                    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                    self.model = genai.GenerativeModel('gemma-3-4b-it')
                else:
                    return "Error: GEMINI_API_KEY not found."
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error querying Gemini: {str(e)}"

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass