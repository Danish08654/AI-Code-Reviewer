import re
import json
from langchain_groq import ChatGroq
from utils.helpers import get_env


class LLMService:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=get_env("GROQ_API_KEY"),
            temperature=0.1
        )

    def generate(self, prompt: str) -> str:
        """
        ALWAYS returns RAW STRING only
        """
        response = self.llm.invoke(prompt)
        return response.content