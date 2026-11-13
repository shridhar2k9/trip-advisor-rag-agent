import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
from typing import Any

from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.types.content import Message

from prompts.system_prompts import SYSTEM_PROMPT
from tools.registry import TOOLS

load_dotenv()  # reads GROQ_API_KEY from a .env file, if present

MODEL_ID = os.getenv("GROQ_MODEL_ID", "openai/gpt-oss-120b")

model = OpenAIModel(
    client_args={
        "api_key": os.environ["GROQ_API_KEY"],
        "base_url": os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),  # or a local OpenAI-compatible server
        "max_retries": 5,  # retry dropped connections (the client default is 2)
    },
    model_id=MODEL_ID,
    # Groq reasoning models stream their thinking by default; hide it so only the answer prints.
    params={"extra_body": {"include_reasoning": False}},
)


def create_travel_agent(
    messages: list[Message] | None = None,
    tools: list[Any] | None = None,
) -> Agent:
    return Agent(
        name="Travel Agent",
        model=model,
        description="Agent for providing travel information and recommendations",
        system_prompt=SYSTEM_PROMPT,
        tools=TOOLS if tools is None else tools,
        messages=messages,
    )


travel_agent = create_travel_agent()
