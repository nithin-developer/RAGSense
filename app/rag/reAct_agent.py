"""
ReAct agent setup for document retrieval and question answering.
"""

import os

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate

from app.config.settings import Config
from app.llms.openai import llm
from app.rag.retriever_setup import get_retriever

config = Config()

# Initialize tools
tools = [get_retriever()]

# Load document description if available
if os.path.exists("description.txt"):
    with open("description.txt", "r", encoding="utf-8") as f:
        description = f.read()
else:
    description = None

# Create ReAct agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", config.prompt("system_prompt")),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])

# Initialize the ReAct agent and executor
react_agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=react_agent,
    tools=tools,
    handle_parsing_errors=True,
    max_iterations=2,
    verbose=True,
    return_intermediate_steps=True
)
