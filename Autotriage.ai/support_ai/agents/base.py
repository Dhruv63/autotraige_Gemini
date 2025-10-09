from abc import ABC, abstractmethod
from typing import Dict, Any
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BaseAgent(ABC):
    """
    A base class for AI agents that initializes and provides an interface
    for querying the Google Gemini Pro model.
    """
    def __init__(self):
        try:
            # Configure the Gemini API key from environment variables
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables.")
            genai.configure(api_key=api_key)
            # Initialize the generative model
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            self.model = None

    def query_llm(self, prompt: str) -> str:
        """
        Sends a prompt to the Gemini API and returns the text response.
        """
        if not self.model:
            return "Error: Generative model not initialized."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"An error occurred while querying the LLM: {e}")
            return f"Error: Could not get a response from the API. Details: {e}"

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass