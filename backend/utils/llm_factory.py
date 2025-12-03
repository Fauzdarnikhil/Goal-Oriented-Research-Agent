import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(model: str = None, temperature: float = 0.3, max_tokens: int = 2000):
    api_key = os.getenv("GROQ_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        raise ValueError("GROQ_API_KEY missing in .env file")

    return ChatGroq(
        model=model or default_model,
        temperature=temperature,
        max_tokens=max_tokens,
        groq_api_key=api_key
    )
