"""
ReAct agent setup for document retrieval and question answering.
"""

import os

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

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

# Create ReAct agent prompt using the standard string template format.
# This avoids the NVIDIA Mistral chat-template error that occurs when
# the last message is from the assistant (agent_scratchpad as an "ai" message).
_system = config.prompt("system_prompt")

_REACT_TEMPLATE = f"""{_system}

You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}"""

prompt = PromptTemplate(
    template=_REACT_TEMPLATE,
    input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
)

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
