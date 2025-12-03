import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIMLClient:
    def __init__(self):
        self.api_key = os.getenv("AIMLAPI_KEY")
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        if self.api_key:
            self.client = OpenAI(
                base_url="https://api.aimlapi.com/v1",
                api_key=self.api_key
            )
        else:
            st.error("Missing AIML API Key! Add it to .env file")
            
    def generate(self, model: str, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return ""
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return ""