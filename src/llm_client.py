import os
from langchain_mistralai import ChatMistralAI

def get_llm_client(api_key: str = None) -> ChatMistralAI:
    key = api_key or os.getenv("MISTRAL_API_KEY")
    return ChatMistralAI(mistral_api_key=key, model="mistral-small-latest", temperature=0.1)
