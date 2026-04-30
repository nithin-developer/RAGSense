"""
NVIDIA NIM LLM initialization using OpenAI-compatible API.
Model: mistralai/mistral-medium-3.5-128b
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

llm = ChatOpenAI(
    model="mistralai/mistral-medium-3.5-128b",
    openai_api_key=NVIDIA_API_KEY,
    openai_api_base=NVIDIA_BASE_URL,
)